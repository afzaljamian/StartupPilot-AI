from ..schemas.models import MarketingOutput
from ..services.llm import GeminiService, GeminiUnavailableError
from ..services.research import TavilyService
from .prompts import MARKETING_SYSTEM
from ..config import settings

class MarketingAgentService:
    def __init__(self):
        self.llm = GeminiService(); self.research = TavilyService()

    async def run(self, idea: str, context: dict | None = None) -> MarketingOutput:
        context = context or {}
        research = await self.research.search(f'{idea} competitors market trends India pricing customer acquisition', 6)
        sources = [{'title': x['title'], 'url': x['url'], 'retrieved_at': x['retrieved_at']} for x in research]
        evidence = '\n'.join(f"- {x['title']}: {x['content'][:1200]} ({x['url']})" for x in research) or 'Live research unavailable — do not invent statistics.'
        if not self.llm.available and settings.demo_mode:
            return self.demo(idea, sources)
        prompt = f'''{MARKETING_SYSTEM}\nStartup idea: {idea}\nOptional context: {context}\nResearch evidence:\n{evidence}\n\nReturn JSON matching the requested schema. Sources must only use supplied research URLs. Clearly label estimates and assumptions.'''
        try:
            return MarketingOutput.model_validate(self.llm.generate_json(prompt, MarketingOutput))
        except GeminiUnavailableError:
            if settings.demo_mode:
                return self.demo(idea, sources)
            raise

    def demo(self, idea: str, sources: list[dict]) -> MarketingOutput:
        return MarketingOutput(
            market_overview='Demo-mode market assessment based on the supplied startup idea; live market statistics are not asserted.',
            target_audience=['College students','Budget-conscious young professionals'],
            ideal_customer_profile=['Age 18–28','Price-sensitive','Mobile-first','Values convenience and healthy choices'],
            customer_pain_points=['Hard to compare options quickly','Unclear pricing','Limited time for research'],
            competitors=[{'name':'Local food-delivery apps','type':'Indirect competitor','note':'Validate local availability and pricing.'},{'name':'Campus canteens','type':'Direct alternative','note':'Often strong on proximity.'}],
            market_opportunities=['Campus-specific discovery','Verified pricing and nutrition information','Student-focused partnerships'],
            go_to_market_strategy=['Pilot at one campus','Partner with local vendors','Use student ambassadors','Measure repeat usage'],
            acquisition_channels=[{'channel':'Campus ambassadors','priority':'High','reason':'Trust and low-cost local reach'},{'channel':'Instagram/Reels','priority':'High','reason':'Student audience fit'},{'channel':'SEO','priority':'Medium','reason':'Capture intent-driven searches'}],
            marketing_budget_allocation=[{'category':'Campus/community','monthly_inr':12000},{'category':'Social content/ads','monthly_inr':10000},{'category':'SEO/tools','monthly_inr':5000},{'category':'Experiments','monthly_inr':3000}],
            ad_copies=['Find affordable healthy meals near campus—compare before you order.','Eat better without overspending. Discover student-friendly meals nearby.','Your campus meal search, simplified.'],
            seo_keywords=['healthy meals near college','affordable student meals','campus food deals','healthy food near campus','student meal finder'],
            content_calendar=[{'day':'1','theme':'Problem','format':'Short video'},{'day':'7','theme':'Vendor spotlight','format':'Carousel'},{'day':'14','theme':'Student budget tips','format':'Post'},{'day':'21','theme':'Healthy meal comparison','format':'Short video'},{'day':'30','theme':'Pilot results','format':'Case study'}],
            sources=sources,
            assumptions=['Demo data is illustrative.','Market size and competitor claims require verification.']
        )
