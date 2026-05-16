"""Agent 1 — NewsParserAgent: Extracts structured metadata from news articles."""

from pydantic import BaseModel

from agents.base import BaseAgent
from agents.prompts import NEWS_PARSER_PROMPT
from config import settings
from schemas.agent_io import NewsParserOutput


class NewsParserAgent(BaseAgent):
    agent_name = "news_parser"
    model = settings.SONNET_MODEL
    system_prompt = NEWS_PARSER_PROMPT

    def get_output_model(self) -> type[BaseModel]:
        return NewsParserOutput
