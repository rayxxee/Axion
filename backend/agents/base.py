"""Abstract base agent with LLM calling and output validation."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from services.llm import call_llm

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all Axion pipeline agents."""

    agent_name: str = "base"
    model: str = ""
    system_prompt: str = ""

    @abstractmethod
    def get_output_model(self) -> type[BaseModel]:
        """Return the Pydantic model class for output validation."""
        ...

    async def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent: call LLM → parse → validate → return dict.

        Args:
            input_data: The input payload (previous agent's output).

        Returns:
            Validated output as a dict.
        """
        logger.info("Agent [%s] starting with model [%s]", self.agent_name, self.model)

        user_message = json.dumps(input_data, ensure_ascii=False)
        raw_output = await call_llm(
            model=self.model,
            system_prompt=self.system_prompt,
            user_message=user_message,
        )

        # Validate against Pydantic model
        output_model = self.get_output_model()
        validated = output_model.model_validate(raw_output)

        result = validated.model_dump()
        logger.info("Agent [%s] completed successfully", self.agent_name)
        return result
