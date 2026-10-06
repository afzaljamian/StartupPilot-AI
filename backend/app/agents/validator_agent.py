from ..schemas.models import ValidationOutput, MarketingOutput, FinanceOutput, ProductOutput
from ..services.llm import GeminiService, GeminiUnavailableError
from ..config import settings
from .prompts import VALIDATOR_SYSTEM

class ValidatorAgentService:
    def __init__(self): self.llm=GeminiService()
    async def run(self, idea: str, marketing: MarketingOutput, finance: FinanceOutput, product: ProductOutput) -> ValidationOutput:
        if not self.llm.available and settings.demo_mode: return self.demo(marketing, finance, product)
        prompt=f'''{VALIDATOR_SYSTEM}\nStartup idea: {idea}\nMARKETING:\n{marketing.model_dump_json()}\nFINANCE:\n{finance.model_dump_json()}\nPRODUCT:\n{product.model_dump_json()}\nCheck statistics/sources, marketing-to-finance assumptions, product-to-budget realism, target/customer alignment, contradictions and technology reasonableness. Unsupported claims must be listed with VERIFY. Return JSON matching schema.'''
        try:
            return ValidationOutput.model_validate(self.llm.generate_json(prompt, ValidationOutput))
        except GeminiUnavailableError:
            if settings.demo_mode:
                return self.demo(marketing, finance, product)
            raise
    def demo(self,m,f,p):
        contradictions=[]; flags=[]; corrections=[]
        m_budget=sum(float(x.get('monthly_inr',0)) for x in m.marketing_budget_allocation)
        f_budget=sum(float(x.get('inr',0)) for x in f.marketing_expenses)
        if abs(m_budget-f_budget)>1: contradictions.append(f'Marketing budget differs: Marketing={m_budget:.0f}/month vs Finance={f_budget:.0f}/month.'); corrections.append('Align the marketing budget between Marketing and Finance.')
        if not m.sources: flags.append('VERIFY: Market and competitor claims have no live sources in this run.')
        flags.append('VERIFY: Demo-mode market assumptions are illustrative, not verified statistics.')
        score=max(0,100-len(contradictions)*15-len(flags)*10)
        status='PASS' if not flags and not contradictions else 'PASS WITH WARNINGS'
        return ValidationOutput(overall_consistency_score=score,marketing_validation=['Structure is complete','Sources are explicitly separated from assumptions'],finance_validation=['Python-generated projections are deterministic','Revenue and expense assumptions are labeled'],product_validation=['MVP scope is small relative to the pilot','User stories match target audience'],cross_agent_consistency=['Marketing and Product target students consistently'],unsupported_claims=['Any unverified market-size or competitor statistic'],verify_flags=flags,contradictions=contradictions,risky_assumptions=['Customer growth rate','Willingness to pay','Vendor acquisition cost'],recommended_corrections=corrections,final_validation_status=status)
