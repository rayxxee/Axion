"""Request schemas for PolicyPulse API."""

from pydantic import BaseModel, Field
from enum import Enum


class InputType(str, Enum):
    """Supported news article input types."""

    TEXT = "text"
    URL = "url"
    PDF = "pdf"


class AnalyzeRequest(BaseModel):
    """Request body for the /analyze endpoint."""

    input_type: InputType
    content: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="Raw article text, URL string, or base64-encoded PDF",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "input_type": "text",
                    "content": "SBP raises interest rate by 200bps effective June 2026",
                }
            ]
        }
    }


class AgentDebugRequest(BaseModel):
    """Request body for individual agent debug endpoints."""

    agent_name: str = Field(
        ...,
        pattern=r"^(news_parser|impact_analyzer|action_generator|executor|output_composer)$",
    )
    input_data: dict = Field(
        ..., description="Raw JSON input for the specific agent"
    )
