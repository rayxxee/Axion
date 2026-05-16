"""Anthropic Claude API wrapper with retry and JSON parsing."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import anthropic

from config import settings

logger = logging.getLogger(__name__)

_client: anthropic.AsyncAnthropic | None = None


def get_client() -> anthropic.AsyncAnthropic:
    """Lazy-init singleton Anthropic client."""
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


async def call_llm(
    model: str,
    system_prompt: str,
    user_message: str,
    max_tokens: int = 4096,
    retries: int = 3,
) -> dict[str, Any]:
    """Call Claude and parse the JSON response.

    Retries up to *retries* times on JSON parse failures.
    Returns the parsed dict.
    """
    client = get_client()
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        start = time.monotonic()
        try:
            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            elapsed = time.monotonic() - start
            raw_text = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            logger.info(
                "LLM call [%s] attempt=%d elapsed=%.2fs "
                "input_tokens=%d output_tokens=%d",
                model,
                attempt,
                elapsed,
                input_tokens,
                output_tokens,
            )

            # Strip markdown fences if the model wraps output
            text = raw_text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text[: text.rfind("```")]
                text = text.strip()

            parsed: dict[str, Any] = json.loads(text)
            return parsed

        except json.JSONDecodeError as exc:
            last_error = exc
            logger.warning(
                "JSON parse failed attempt=%d/%d: %s",
                attempt,
                retries,
                exc,
            )
        except anthropic.APIError as exc:
            last_error = exc
            logger.error("Anthropic API error attempt=%d/%d: %s", attempt, retries, exc)
            if attempt < retries:
                await _backoff(attempt)

    raise RuntimeError(
        f"LLM call failed after {retries} attempts: {last_error}"
    ) from last_error


async def _backoff(attempt: int) -> None:
    """Exponential backoff between retries."""
    import asyncio
    delay = min(2**attempt, 10)
    await asyncio.sleep(delay)
