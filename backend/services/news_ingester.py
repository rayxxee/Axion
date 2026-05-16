"""URL scraping utility for article ingestion."""

from __future__ import annotations

import logging

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def fetch_article_from_url(url: str, timeout: float = 15.0) -> str | None:
    """Fetch a URL and extract article text using BeautifulSoup.

    Returns cleaned plain text, or None on failure.
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Try to find article body
        article = soup.find("article") or soup.find("main") or soup.body
        if article is None:
            return soup.get_text(separator="\n", strip=True)

        text = article.get_text(separator="\n", strip=True)
        logger.info("Scraped %d chars from %s", len(text), url)
        return text if len(text) > 20 else None

    except Exception as exc:
        logger.error("Failed to scrape %s: %s", url, exc)
        return None
