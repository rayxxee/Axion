"""PDF text extraction utility for article ingestion."""

from __future__ import annotations

import io
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_bytes: bytes) -> str | None:
    """Extract text from PDF bytes using PyMuPDF (fitz).

    Returns cleaned plain text, or None on failure.
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text_parts = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                text_parts.append(text.strip())

        doc.close()

        full_text = "\n\n".join(text_parts)
        logger.info("Extracted %d chars from PDF (%d pages)", len(full_text), len(text_parts))

        return full_text if len(full_text) > 20 else None

    except ImportError:
        logger.error("PyMuPDF (fitz) not installed. Run: pip install PyMuPDF")
        return None
    except Exception as exc:
        logger.error("Failed to extract PDF text: %s", exc)
        return None
