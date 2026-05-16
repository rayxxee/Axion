"""Pipeline orchestrator — chains all 5 agents sequentially."""

from __future__ import annotations

import logging
from typing import Any

from agents.news_parser import NewsParserAgent
from agents.impact_analyzer import ImpactAnalyzerAgent
from agents.action_generator import ActionGeneratorAgent
from agents.executor import ExecutorAgent
from agents.output_composer import OutputComposerAgent
from schemas.requests import AnalyzeRequest, InputType
from services import firestore_client, job_store
from services.scraper import scrape_url, extract_pdf

logger = logging.getLogger(__name__)


async def run_pipeline(job_id: str, request: AnalyzeRequest) -> None:
    """Run the full 5-agent analysis pipeline.

    Updates job_store with SSE events at each stage.
    """
    try:
        # ── Step 0: Preprocess input ──
        if request.input_type == InputType.URL:
            article_text = await scrape_url(request.content)
        elif request.input_type == InputType.PDF:
            article_text = extract_pdf(request.content)
        else:
            article_text = request.content

        raw_input = {"article_text": article_text}

        # ── Agent 1: NewsParser ──
        await job_store.update_job(job_id, "agent_start", agent="news_parser")
        agent1 = NewsParserAgent()
        news_output = await agent1.run(raw_input)
        await job_store.update_job(
            job_id, "agent_complete", agent="news_parser", data=news_output
        )

        # ── Agent 2: ImpactAnalyzer ──
        await job_store.update_job(job_id, "agent_start", agent="impact_analyzer")
        agent2 = ImpactAnalyzerAgent()
        impact_output = await agent2.run(news_output)
        await job_store.update_job(
            job_id, "agent_complete", agent="impact_analyzer", data=impact_output
        )

        # ── Agent 3: ActionGenerator ──
        await job_store.update_job(job_id, "agent_start", agent="action_generator")
        agent3 = ActionGeneratorAgent()
        actions_output = await agent3.run(impact_output)
        await job_store.update_job(
            job_id, "agent_complete", agent="action_generator", data=actions_output
        )

        # ── Agent 4: Executor (3 sub-agents in parallel) ──
        await job_store.update_job(job_id, "agent_start", agent="executor")
        agent4 = ExecutorAgent()
        executor_output = await agent4.run(impact_output, actions_output)

        # Patch the Firestore write with actual job_id
        pricing_updates = executor_output.get("pricing", {}).get("product_updates", [])
        if pricing_updates:
            await firestore_client.write_pricing_records(job_id, pricing_updates)

        await job_store.update_job(
            job_id, "agent_complete", agent="executor", data=executor_output
        )

        # ── Agent 5: OutputComposer ──
        await job_store.update_job(job_id, "agent_start", agent="output_composer")
        agent5 = OutputComposerAgent()
        composer_input = {
            "news_parser": news_output,
            "impact_analyzer": impact_output,
            "action_generator": actions_output,
            "executor": executor_output,
        }
        final_report = await agent5.run(composer_input)
        await job_store.update_job(
            job_id, "agent_complete", agent="output_composer", data=final_report
        )

        # ── Save final report ──
        await firestore_client.save_job(job_id, {
            "status": "completed",
            "input_type": request.input_type.value,
            "input_content": request.content[:5000],
            "agent_outputs": {
                "news_parser": news_output,
                "impact_analyzer": impact_output,
                "action_generator": actions_output,
                "executor": executor_output,
                "output_composer": final_report,
            },
        })

        await job_store.update_job(
            job_id, "pipeline_done", data=final_report
        )

        logger.info("Pipeline completed for job %s", job_id)

    except Exception as exc:
        logger.exception("Pipeline failed for job %s", job_id)
        await job_store.update_job(
            job_id, "error", data={"message": str(exc)}
        )
