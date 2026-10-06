from ..schemas.models import ProductOutput, MarketingOutput, FinanceOutput
from ..services.llm import GeminiService, GeminiUnavailableError
from ..config import settings
from .prompts import PRODUCT_SYSTEM

class ProductAgentService:
    def __init__(self): self.llm=GeminiService()
    async def run(self, idea: str, marketing: MarketingOutput, finance: FinanceOutput) -> ProductOutput:
        if not self.llm.available and settings.demo_mode: return self.demo(idea, marketing, finance)
        prompt=f'''{PRODUCT_SYSTEM}\nStartup idea: {idea}\nMarketing analysis:\n{marketing.model_dump_json()}\nFinancial analysis:\n{finance.model_dump_json()}\nCreate a realistic MVP aligned with target users and budget. Return JSON matching the schema.'''
        try:
            return ProductOutput.model_validate(self.llm.generate_json(prompt, ProductOutput))
        except GeminiUnavailableError:
            if settings.demo_mode:
                return self.demo(idea, marketing, finance)
            raise
    def demo(self, idea, marketing, finance):
        return ProductOutput(product_overview='A mobile-first web platform for discovering and comparing affordable healthy meal options around a college campus.',problem_statement='Students need a fast, trustworthy way to compare nearby meals by price, health preference and distance.',target_users=marketing.target_audience,product_goals=['Validate student demand','Onboard initial vendors','Enable fast comparison','Measure repeat usage'],mvp_features=[{'name':'Meal discovery','priority':'Must Have'},{'name':'Filters for price/diet','priority':'Must Have'},{'name':'Vendor profile','priority':'Must Have'},{'name':'Saved meals','priority':'Should Have'},{'name':'Reviews','priority':'Should Have'},{'name':'Personalized recommendations','priority':'Could Have'}],feature_prioritization={'Must Have':['Meal discovery','Price/diet filters','Vendor profile'],'Should Have':['Saved meals','Reviews'],'Could Have':['Personalized recommendations'],'Won\'t Have':['Native mobile app','Payments in MVP']},user_stories=['As a student, I want to compare nearby healthy meals so that I can choose quickly.','As a student, I want to filter meals by price so that I stay within budget.','As a student, I want to filter by dietary preference so that results fit my needs.','As a vendor, I want to publish my menu so that students can discover it.','As a founder, I want to see usage metrics so that I can improve the pilot.'],roadmap=[{'month':'Month 1','focus':'MVP build','deliverables':['Discovery','Filters','Vendor pages','Analytics']},{'month':'Month 2','focus':'Campus pilot','deliverables':['Vendor onboarding','Student ambassadors','Feedback loops']},{'month':'Month 3','focus':'Optimization','deliverables':['Retention improvements','Pricing tests','Scale readiness']}],kpi_targets=[{'kpi':'Weekly active students','target':'500 by pilot end'},{'kpi':'Repeat usage','target':'>25%'},{'kpi':'Vendor onboarding','target':'30 pilot vendors'}],technology_stack=['React','FastAPI','MongoDB','Redis/Celery','Gemini API'],product_risks=['Insufficient vendor coverage','Low repeat usage','Data freshness'],future_features=['Personalized recommendations','Native app','Payments'],assumptions=['MVP should remain small enough for the proposed pilot budget.'])
