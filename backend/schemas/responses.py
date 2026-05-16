"""Response schemas for Axion API."""

from pydantic import BaseModel
from typing import Optional

from .agent_io import FinalReport


class AnalyzeResponse(BaseModel):
    """Returned immediately when analysis is kicked off."""

    job_id: str
    status: str = "processing"
    message: str = "Pipeline started. Connect to SSE stream for progress."
    stream_url: str


class JobResult(BaseModel):
    """Returned when polling for a completed job."""

    job_id: str
    status: str  # "completed" | "failed" | "processing"
    report: Optional[FinalReport] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    detail: str
    error_code: str
