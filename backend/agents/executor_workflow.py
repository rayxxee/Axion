"""Agent 4c — WorkflowTriggerer: Generates structured workflow alert payloads."""

from pydantic import BaseModel

from agents.base import BaseAgent
from agents.prompts import WORKFLOW_TRIGGERER_PROMPT
from config import settings
from schemas.agent_io import WorkflowTriggererOutput


class WorkflowTriggererAgent(BaseAgent):
    agent_name = "workflow_triggerer"
    model = settings.SONNET_MODEL
    system_prompt = WORKFLOW_TRIGGERER_PROMPT

    def get_output_model(self) -> type[BaseModel]:
        return WorkflowTriggererOutput
