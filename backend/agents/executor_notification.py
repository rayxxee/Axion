"""Agent 4b — NotificationDrafter: Generates email, SMS, and push templates."""

from pydantic import BaseModel

from agents.base import BaseAgent
from agents.prompts import NOTIFICATION_DRAFTER_PROMPT
from config import settings
from schemas.agent_io import NotificationDrafterOutput


class NotificationDrafterAgent(BaseAgent):
    agent_name = "notification_drafter"
    model = settings.SONNET_MODEL
    system_prompt = NOTIFICATION_DRAFTER_PROMPT

    def get_output_model(self) -> type[BaseModel]:
        return NotificationDrafterOutput
