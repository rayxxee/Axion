"""Agent 2 — ImpactAnalyzerAgent: Quantifies business impact of economic signals."""

from pydantic import BaseModel

from agents.base import BaseAgent
from agents.prompts import IMPACT_ANALYZER_PROMPT
from config import settings
from schemas.agent_io import ImpactAnalyzerOutput


class ImpactAnalyzerAgent(BaseAgent):
    agent_name = "impact_analyzer"
    model = settings.SONNET_MODEL
    system_prompt = IMPACT_ANALYZER_PROMPT

    def get_output_model(self) -> type[BaseModel]:
        return ImpactAnalyzerOutput
