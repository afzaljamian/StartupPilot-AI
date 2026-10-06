import asyncio

# Keep one event loop alive for the lifetime of each Celery worker process.
# Motor/AsyncIOMotorClient binds its executor to the loop it first uses;
# asyncio.run() would close that loop after every task and make subsequent
# tasks fail with 'Event loop is closed'.
_worker_loop = asyncio.new_event_loop()
from datetime import datetime, timezone
from .celery_app import celery_app
from ..database.mongodb import update_run, save_report, get_run
from ..agents.marketing_agent import MarketingAgentService
from ..agents.finance_agent import FinanceAgentService
from ..agents.product_agent import ProductAgentService
from ..agents.validator_agent import ValidatorAgentService
from ..agents.crew import crewai_available, run_crewai_pipeline
from ..services.research import TavilyService
from ..services.calculations import build_financial_model
from ..services.llm import GeminiUnavailableError
from ..services.websocket_manager import publish_sync
from ..config import settings

async def _run(run_id: str):
    async def step(status, message):
        await update_run(run_id,status=status)
        publish_sync(run_id,{'type':'status','run_id':run_id,'status':status,'message':message})
    try:
        run=await get_run(run_id); idea=run['startup_idea']
        used_fallback = False
        if crewai_available() and not settings.demo_mode:
            research_marketing=await TavilyService().search(f'{idea} competitors market trends customer acquisition India',6)
            research_finance=await TavilyService().search(f'{idea} pricing benchmark startup costs CAC unit economics India',6)
            research=[{'agent':'marketing',**x} for x in research_marketing]+[{'agent':'finance',**x} for x in research_finance]
            await step('marketing_running','CrewAI Manager started Marketing Agent...')
            try:
                marketing,finance,product,validation=await asyncio.to_thread(run_crewai_pipeline,idea,research)
                await step('marketing_completed','Marketing Agent completed')
                await step('finance_running','Finance Agent completed with Marketing context')
                # Replace any LLM arithmetic with deterministic Python calculations.
                model=build_financial_model(finance.revenue_assumptions)
                finance.year1_projection=model['year1_projection']; finance.break_even=model['break_even']
                await step('finance_completed','Finance calculations verified by Python')
                await step('product_running','Product Agent completed with Marketing + Finance context')
                await step('product_completed','Product Agent completed')
                await step('validation_running','Validator Agent checking consistency...')
            except GeminiUnavailableError:
                used_fallback = True
                await step('fallback_running','Gemini is temporarily unavailable. Switching to fallback responses so the workflow can complete.')
                sources=[{'title':x['title'],'url':x['url'],'retrieved_at':x['retrieved_at']} for x in research_marketing]
                marketing = MarketingAgentService().demo(idea, sources)
                await step('marketing_completed','Marketing Agent completed using fallback responses')
                await step('finance_running','Finance Agent building deterministic fallback model...')
                finance = FinanceAgentService().demo(marketing, sources)
                await step('finance_completed','Finance calculations verified by Python')
                await step('product_running','Product Agent preparing fallback MVP strategy...')
                product = ProductAgentService().demo(idea, marketing, finance)
                await step('product_completed','Product Agent completed using fallback responses')
                await step('validation_running','Validator Agent checking fallback outputs...')
                validation = ValidatorAgentService().demo(marketing, finance, product)
                await step('validation_completed','Validation completed using fallback responses')
        else:
            # Explicit Demo Mode always uses clearly simulated responses.
            # If live AI is requested but CrewAI/Gemini is unavailable, use the
            # same safe fallback so the college demo can still complete.
            used_fallback = True
            if settings.demo_mode:
                await step('fallback_running','Demo Mode enabled — using simulated AI responses.')
            else:
                await step('fallback_running','Live AI is unavailable. Using fallback responses so the workflow can complete.')
            marketing = MarketingAgentService().demo(idea, [])
            await step('marketing_completed','Marketing Agent completed using fallback responses')
            await step('finance_running','Finance Agent building deterministic fallback model...')
            finance = FinanceAgentService().demo(marketing, [])
            await step('finance_completed','Finance calculations verified by Python')
            await step('product_running','Product Agent preparing fallback MVP strategy...')
            product = ProductAgentService().demo(idea, marketing, finance)
            await step('product_completed','Product Agent completed using fallback responses')
            await step('validation_running','Validator Agent checking fallback outputs...')
            validation = ValidatorAgentService().demo(marketing, finance, product)
            await step('validation_completed','Validation completed using fallback responses')
        report={'startup_idea':idea,'marketing':marketing.model_dump(),'finance':finance.model_dump(),'product':product.model_dump(),'validation':validation.model_dump(),'sources':marketing.model_dump().get('sources',[])+finance.model_dump().get('sources',[]),'generated_at':datetime.now(timezone.utc),'demo_mode': settings.demo_mode and not bool(settings.gemini_api_key) or used_fallback, 'execution_mode': 'fallback_demo' if used_fallback else ('demo_mode' if settings.demo_mode else 'live_ai')}
        await save_report(run_id,report)
        await update_run(run_id,status='completed',completed_at=datetime.now(timezone.utc))
        publish_sync(run_id,{'type':'status','run_id':run_id,'status':'completed','message':'Business plan ready'})
    except Exception:
        await update_run(run_id,status='failed',error='Analysis could not be completed. Please retry.')
        publish_sync(run_id,{'type':'status','run_id':run_id,'status':'failed','message':'Analysis failed. Please retry.'})
        raise

@celery_app.task(name='startuppilot.run_analysis')
def run_analysis(run_id: str):
    asyncio.set_event_loop(_worker_loop)
    return _worker_loop.run_until_complete(_run(run_id))
