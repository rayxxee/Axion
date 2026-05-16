"""NewsAPI client for fetching related articles."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from config import settings

logger = logging.getLogger(__name__)

NEWS_API_BASE = "https://newsapi.org/v2"


async def search_news(query: str, page_size: int = 5) -> list[dict[str, Any]]:
    """Search NewsAPI for articles matching the query.

    Returns list of article dicts. Falls back to empty list on failure.
    """
    if not settings.NEWS_API_KEY:
        logger.warning("NEWS_API_KEY not set — skipping NewsAPI search")
        return []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{NEWS_API_BASE}/everything",
                params={
                    "q": query,
                    "pageSize": page_size,
                    "sortBy": "publishedAt",
                    "apiKey": settings.NEWS_API_KEY,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("articles", [])

    except Exception as exc:
        logger.error("NewsAPI search failed: %s", exc)
        return []
