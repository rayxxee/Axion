"""URL scraping and PDF text extraction utilities."""

from __future__ import annotations

import base64
import io
import logging

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def scrape_url(url: str, timeout: float = 15.0) -> str:
    """Fetch a URL and extract article text using BeautifulSoup.

    Returns cleaned plain text.
    """
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

    return article.get_text(separator="\n", strip=True)


def extract_pdf(base64_content: str) -> str:
    """Decode base64 PDF and extract text from all pages.

    Returns concatenated page text.
    """
    try:
        from PyPDF2 import PdfReader
    except ImportError as exc:
        raise RuntimeError("PyPDF2 required for PDF extraction") from exc

    pdf_bytes = base64.b64decode(base64_content)
    reader = PdfReader(io.BytesIO(pdf_bytes))

    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())

    full_text = "\n\n".join(pages)
    logger.info("Extracted %d chars from %d PDF pages", len(full_text), len(reader.pages))
    return full_text
