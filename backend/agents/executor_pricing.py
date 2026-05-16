"""Agent 4a — PricingUpdater: Generates before/after product pricing adjustments."""

from pydantic import BaseModel

from agents.base import BaseAgent
from agents.prompts import PRICING_UPDATER_PROMPT
from config import settings
from schemas.agent_io import PricingUpdaterOutput


class PricingUpdaterAgent(BaseAgent):
    agent_name = "pricing_updater"
    model = settings.SONNET_MODEL
    system_prompt = PRICING_UPDATER_PROMPT

    def get_output_model(self) -> type[BaseModel]:
        return PricingUpdaterOutput
