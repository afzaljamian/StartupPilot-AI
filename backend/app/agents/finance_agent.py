from ..schemas.models import FinanceOutput, MarketingOutput
from ..services.llm import GeminiService, GeminiUnavailableError
from ..services.research import TavilyService
from ..services.calculations import build_financial_model
from .prompts import FINANCE_SYSTEM
from ..config import settings

class FinanceAgentService:
    def __init__(self): self.llm=GeminiService(); self.research=TavilyService()

    async def run(self, idea: str, marketing: MarketingOutput) -> FinanceOutput:
        research = await self.research.search(f'{idea} pricing benchmark startup customer acquisition cost India', 5)
        sources=[{'title':x['title'],'url':x['url'],'retrieved_at':x['retrieved_at']} for x in research]
        if not self.llm.available and settings.demo_mode:
            return self.demo(marketing, sources)
        prompt=f'''{FINANCE_SYSTEM}\nStartup idea: {idea}\nMarketing output:\n{marketing.model_dump_json()}\nExternal research:\n{research}\nProvide explicit assumptions and source-backed facts. Give revenue_per_customer, starting_customers, monthly_growth_rate, variable_cost_per_customer, fixed_monthly_cost, marketing_monthly_cost and initial_setup_cost assumptions so Python can calculate the 12-month model. Return JSON matching the schema.'''
        try:
            raw=self.llm.generate_json(prompt, FinanceOutput)
        except GeminiUnavailableError:
            if settings.demo_mode:
                return self.demo(marketing, sources)
            raise
        output=FinanceOutput.model_validate(raw)
        model=build_financial_model(output.revenue_assumptions)
        output.year1_projection=model['year1_projection']; output.break_even=model['break_even']
        return output

    def demo(self, marketing, sources):
        assumptions={'revenue_per_customer':299,'starting_customers':100,'monthly_growth_rate':0.20,'variable_cost_per_customer':90,'fixed_monthly_cost':90000,'marketing_monthly_cost':30000,'initial_setup_cost':250000}
        model=build_financial_model(assumptions)
        return FinanceOutput(executive_summary='Illustrative demo financial model. All values are assumptions, not verified market facts.',revenue_models=[{'name':'Vendor commission','description':'Percentage fee per transaction'},{'name':'Premium vendor subscription','description':'Monthly SaaS plan for vendors'},{'name':'Sponsored listings','description':'Paid discovery placements'}],recommended_revenue_model='Vendor commission + optional vendor subscription',initial_startup_costs=[{'item':'MVP development/setup','inr':150000},{'item':'Branding/legal/admin allowance','inr':50000},{'item':'Launch experiments','inr':50000}],monthly_operating_expenses=[{'item':'Engineering/tools','inr':50000},{'item':'Operations','inr':25000},{'item':'Cloud/software','inr':15000}],marketing_expenses=marketing.marketing_budget_allocation,revenue_assumptions=assumptions,year1_projection=model['year1_projection'],break_even=model['break_even'],funding_requirements={'recommended_initial_runway_inr':1000000,'runway_months':9},funding_path='Bootstrap the pilot, validate retention, then consider a small pre-seed round.',financial_risks=['Low early conversion','Vendor acquisition costs','Demand seasonality','Assumption sensitivity'],assumptions=['All figures are illustrative.','Actual CAC and willingness-to-pay require pilot validation.'],sources=sources)
