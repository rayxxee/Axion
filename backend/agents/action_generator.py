"""Agent 3 — ActionGeneratorAgent: Generates ranked business actions."""

from pydantic import BaseModel

from agents.base import BaseAgent
from agents.prompts import ACTION_GENERATOR_PROMPT
from config import settings
from schemas.agent_io import ActionGeneratorOutput


class ActionGeneratorAgent(BaseAgent):
    agent_name = "action_generator"
    model = settings.OPUS_MODEL  # Uses Opus for complex strategic reasoning
    system_prompt = ACTION_GENERATOR_PROMPT

    def get_output_model(self) -> type[BaseModel]:
        return ActionGeneratorOutput
