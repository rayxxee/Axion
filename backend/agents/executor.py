"""Agent 4 — ExecutorAgent: Orchestrates 3 sub-agents in parallel."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from pydantic import BaseModel

from agents.executor_pricing import PricingUpdaterAgent
from agents.executor_notification import NotificationDrafterAgent
from agents.executor_workflow import WorkflowTriggererAgent
from schemas.agent_io import ExecutorOutput
from services import firestore_client

logger = logging.getLogger(__name__)


class ExecutorAgent:
    """Runs PricingUpdater, NotificationDrafter, and WorkflowTriggerer in parallel."""

    agent_name = "executor"

    def __init__(self) -> None:
        self.pricing_agent = PricingUpdaterAgent()
        self.notification_agent = NotificationDrafterAgent()
        self.workflow_agent = WorkflowTriggererAgent()

    async def run(
        self,
        impact_output: dict[str, Any],
        actions_output: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute all 3 sub-agents concurrently.

        Args:
            impact_output: Agent 2 output (quantified metrics + severity).
            actions_output: Agent 3 output (ranked actions list).

        Returns:
            Combined ExecutorOutput dict.
        """
        # Build input for sub-agents: impact context + top simulatable action
        top_action = next(
            (a for a in actions_output.get("actions", []) if a.get("simulate")),
            actions_output.get("actions", [{}])[0],
        )

        sub_input = {
            "impact": impact_output,
            "top_action": top_action,
            "all_actions": actions_output.get("actions", []),
        }

        logger.info("Executor launching 3 sub-agents in parallel")

        # Run all three sub-agents concurrently
        pricing_result, notification_result, workflow_result = await asyncio.gather(
            self.pricing_agent.run(sub_input),
            self.notification_agent.run(sub_input),
            self.workflow_agent.run(sub_input),
        )

        # Write pricing records to Firestore
        product_updates = pricing_result.get("product_updates", [])
        if product_updates:
            await firestore_client.write_pricing_records(
                job_id="current",  # Replaced by pipeline with actual job_id
                records=product_updates,
            )

        # Validate combined output
        combined = {
            "pricing": pricing_result,
            "notification": notification_result,
            "workflow": workflow_result,
        }

        validated = ExecutorOutput.model_validate(combined)
        result = validated.model_dump()

        logger.info("Executor completed all 3 sub-agents")
        return result
