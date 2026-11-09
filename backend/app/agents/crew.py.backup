"""Live CrewAI orchestration.

The project uses a deterministic sequential CrewAI process because the domain outputs
have hard dependencies: Finance needs Marketing, Product needs Marketing+Finance, and
Validator needs all three. A coordinator/manager agent defines the operating contract,
while the CrewAI process enforces the dependency order.
"""
import json
from ..config import settings
from ..services.llm import GeminiUnavailableError
import random
import time

def crewai_available() -> bool:
    try:
        import crewai
        return bool(settings.gemini_api_key)
    except Exception:
        return False

def _parse(text: str):
    text=text.strip()
    if text.startswith('```'):
        text=text.split('\n',1)[1].rsplit('```',1)[0]
    try: return json.loads(text)
    except json.JSONDecodeError:
        start=text.find('{'); end=text.rfind('}')
        if start>=0 and end>start: return json.loads(text[start:end+1])
        raise

def run_crewai_pipeline(idea: str, research: list[dict]):
    from crewai import Agent, Task, Crew, Process, LLM
    from ..schemas.models import MarketingOutput, FinanceOutput, ProductOutput, ValidationOutput
    llm=LLM(model=f'gemini/{settings.gemini_model}',api_key=settings.gemini_api_key,temperature=0.2)
    coordinator=Agent(role='StartupPilot Manager',goal='Coordinate specialist startup analysis while preserving dependency order.',backstory='You enforce a strict handoff contract between independent startup specialists.',llm=llm,allow_delegation=False,verbose=False)
    marketing=Agent(role='Startup Marketing Strategist',goal='Create research-backed marketing strategy without fabricated statistics.',backstory='Specialist in customer discovery, GTM and growth.',llm=llm,allow_delegation=False,verbose=False)
    finance=Agent(role='Startup Financial Analyst',goal='Create a financially coherent model using the completed marketing analysis.',backstory='Specialist in early-stage unit economics and startup finance.',llm=llm,allow_delegation=False,verbose=False)
    product=Agent(role='Startup Product Manager',goal='Define an MVP constrained by customer needs and financial reality.',backstory='Specialist in MVP scope and product roadmaps.',llm=llm,allow_delegation=False,verbose=False)
    validator=Agent(role='Business Plan Quality and Consistency Validator',goal='Audit all outputs and flag unsupported claims and contradictions.',backstory='Independent quality assurance reviewer.',llm=llm,allow_delegation=False,verbose=False)
    evidence=json.dumps(research)
    t1=Task(description=f'''Analyze startup idea: {idea}\nResearch evidence: {evidence}\nReturn ONLY valid JSON matching this schema: {MarketingOutput.model_json_schema()}. Separate facts, estimates and assumptions. Unsupported statistics must say Data unavailable — requires verification.''',expected_output='Valid MarketingOutput JSON',agent=marketing)
    t2=Task(description=f'''Using the original idea and the completed Marketing task, build the financial plan. Marketing context is mandatory. Return ONLY valid JSON matching: {FinanceOutput.model_json_schema()}. Include explicit calculation inputs. Do not invent statistics.''',expected_output='Valid FinanceOutput JSON',agent=finance,context=[t1])
    t3=Task(description=f'''Using the original idea plus Marketing and Finance outputs, create the product requirements document. Return ONLY valid JSON matching: {ProductOutput.model_json_schema()}. Include at least five user stories and MoSCoW priorities.''',expected_output='Valid ProductOutput JSON',agent=product,context=[t1,t2])
    t4=Task(description=f'''Audit the Marketing, Finance and Product outputs. Do not create a new business plan. Return ONLY valid JSON matching: {ValidationOutput.model_json_schema()}. Flag unsupported claims as VERIFY and find contradictions.''',expected_output='Valid ValidationOutput JSON',agent=validator,context=[t1,t2,t3])
    crew=Crew(agents=[coordinator,marketing,finance,product,validator],tasks=[t1,t2,t3,t4],process=Process.sequential,verbose=False)
    last_exc = None
    for attempt in range(4):
        try:
            crew.kickoff()
            last_exc = None
            break
        except Exception as exc:
            last_exc = exc
            text = str(exc).lower()
            transient = any(token in text for token in (
                "503", "unavailable", "high demand", "429", "resource exhausted",
                "500", "internal server error", "temporarily"
            ))
            if not transient or attempt == 3:
                break
            time.sleep(min(16, 2 ** attempt) + random.uniform(0.2, 0.8))
    if last_exc is not None:
        text = str(last_exc).lower()
        if any(token in text for token in (
            "503", "unavailable", "high demand", "429", "resource exhausted",
            "500", "internal server error", "temporarily"
        )):
            raise GeminiUnavailableError(
                "Gemini remained unavailable after CrewAI retries."
            ) from last_exc
        raise last_exc
    outputs=[t.output.raw for t in [t1,t2,t3,t4]]
    return MarketingOutput.model_validate(_parse(outputs[0])),FinanceOutput.model_validate(_parse(outputs[1])),ProductOutput.model_validate(_parse(outputs[2])),ValidationOutput.model_validate(_parse(outputs[3]))
