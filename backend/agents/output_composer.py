"""Agent 5 — OutputComposer: Synthesizes all agent outputs into the final report."""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel

from agents.base import BaseAgent
from agents.prompts import OUTPUT_COMPOSER_PROMPT
from config import settings
from schemas.agent_io import FinalReport

logger = logging.getLogger(__name__)


class OutputComposerAgent(BaseAgent):
    agent_name = "output_composer"
    model = settings.SONNET_MODEL
    system_prompt = OUTPUT_COMPOSER_PROMPT

    def get_output_model(self) -> type[BaseModel]:
        return FinalReport

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Override to pass all 4 previous agent outputs as combined context.

        input_data should have keys: news_parser, impact_analyzer,
        action_generator, executor.
        """
        logger.info("OutputComposer assembling final report from %d agent outputs",
                     len(input_data))
        return await super().run(input_data)
