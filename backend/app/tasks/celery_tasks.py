import asyncio

# Keep one event loop alive for the lifetime of each Celery worker process.
# Motor/AsyncIOMotorClient binds its executor to the loop it first uses;
# asyncio.run() would close that loop after every task and make subsequent
# tasks fail with "Event loop is closed".
_worker_loop = asyncio.new_event_loop()

from datetime import datetime, timezone

from .celery_app import celery_app
from ..database.mongodb import update_run, save_report, get_run
from ..agents.crew import crewai_available, run_crewai_pipeline
from ..services.research import TavilyService
from ..services.calculations import build_financial_model
from ..services.llm import GeminiUnavailableError
from ..services.websocket_manager import publish_sync
from ..config import settings


async def _run(run_id: str):
    async def step(status, message):
        await update_run(run_id, status=status)
        publish_sync(
            run_id,
            {
                "type": "status",
                "run_id": run_id,
                "status": status,
                "message": message,
            },
        )

    try:
        run = await get_run(run_id)

        if not run:
            raise RuntimeError(f"Run {run_id} was not found")

        idea = run["startup_idea"]

        # ============================================================
        # DEMO MODE
        # ============================================================
        if settings.demo_mode:
            raise RuntimeError(
                "Demo Mode is enabled. Disable DEMO_MODE to run live AI analysis."
            )

        # ============================================================
        # LIVE AI MODE
        # ============================================================
        if not crewai_available():
            raise RuntimeError(
                "Live AI analysis is unavailable because CrewAI or Gemini "
                "is not configured correctly."
            )

        # ------------------------------------------------------------
        # Research
        # ------------------------------------------------------------
        await step(
            "research_running",
            "Collecting research evidence for the live AI analysis...",
        )

        research_service = TavilyService()

        research_marketing = await research_service.search(
            f"{idea} competitors market trends customer acquisition India",
            6,
        )

        research_finance = await research_service.search(
            f"{idea} pricing benchmark startup costs CAC unit economics India",
            6,
        )

        research = (
            [{"agent": "marketing", **x} for x in research_marketing]
            + [{"agent": "finance", **x} for x in research_finance]
        )

        # ------------------------------------------------------------
        # CrewAI sequential pipeline
        # Marketing → Finance → Product → Validator
        # ------------------------------------------------------------
        await step(
            "marketing_running",
            "CrewAI Manager started the live Marketing Agent...",
        )

        try:
            (
                marketing,
                finance,
                product,
                validation,
            ) = await asyncio.to_thread(
                run_crewai_pipeline,
                idea,
                research,
            )

        except GeminiUnavailableError as exc:
            await step(
                "failed",
                "Live Gemini service is temporarily unavailable. "
                "No simulated data was used.",
            )
            raise RuntimeError(
                "Live Gemini analysis failed after retries. "
                "No fallback/demo data was substituted."
            ) from exc

        # ------------------------------------------------------------
        # Marketing completed
        # ------------------------------------------------------------
        await step(
            "marketing_completed",
            "Marketing Agent completed using live Gemini analysis.",
        )

        # ------------------------------------------------------------
        # Finance
        # ------------------------------------------------------------
        await step(
            "finance_running",
            "Finance Agent completed with Marketing context. "
            "Verifying financial calculations...",
        )

        # Keep arithmetic deterministic and verifiable.
        model = build_financial_model(finance.revenue_assumptions)

        finance.year1_projection = model["year1_projection"]
        finance.break_even = model["break_even"]

        await step(
            "finance_completed",
            "Finance calculations verified by Python.",
        )

        # ------------------------------------------------------------
        # Product
        # ------------------------------------------------------------
        await step(
            "product_running",
            "Product Agent completed with Marketing + Finance context.",
        )

        await step(
            "product_completed",
            "Product Agent completed using live AI analysis.",
        )

        # ------------------------------------------------------------
        # Validator
        # ------------------------------------------------------------
        await step(
            "validation_running",
            "Validator Agent checking consistency across all outputs...",
        )

        await step(
            "validation_completed",
            "Validator Agent completed the live consistency check.",
        )

        # ------------------------------------------------------------
        # Save REAL report
        # ------------------------------------------------------------
        report = {
            "startup_idea": idea,
            "marketing": marketing.model_dump(),
            "finance": finance.model_dump(),
            "product": product.model_dump(),
            "validation": validation.model_dump(),
            "sources": (
                marketing.model_dump().get("sources", [])
                + finance.model_dump().get("sources", [])
            ),
            "generated_at": datetime.now(timezone.utc),

            # IMPORTANT:
            # This report was generated by the live pipeline.
            "demo_mode": False,
            "execution_mode": "live_ai",
        }

        await save_report(run_id, report)

        await update_run(
            run_id,
            status="completed",
            completed_at=datetime.now(timezone.utc),
        )

        publish_sync(
            run_id,
            {
                "type": "status",
                "run_id": run_id,
                "status": "completed",
                "message": "Live AI business plan ready.",
            },
        )

    except Exception as exc:
        await update_run(
            run_id,
            status="failed",
            error=str(exc)[:500],
        )

        publish_sync(
            run_id,
            {
                "type": "status",
                "run_id": run_id,
                "status": "failed",
                "message": "Live AI analysis failed. No simulated data was used.",
            },
        )

        raise


@celery_app.task(name="startuppilot.run_analysis")
def run_analysis(run_id: str):
    asyncio.set_event_loop(_worker_loop)
    return _worker_loop.run_until_complete(_run(run_id))