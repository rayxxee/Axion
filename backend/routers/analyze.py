"""Analysis routes — main pipeline entry point + SSE stream."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse

from schemas.requests import AnalyzeRequest
from schemas.responses import AnalyzeResponse, JobResult
from services import job_store
from services.pipeline import run_pipeline

router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse, status_code=202)
async def start_analysis(req: AnalyzeRequest, bg: BackgroundTasks):
    """Kick off the 5-agent analysis pipeline.

    Returns immediately with a job_id and SSE stream URL.
    """
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id)
    bg.add_task(run_pipeline, job_id, req)

    return AnalyzeResponse(
        job_id=job_id,
        stream_url=f"/api/v1/analyze/{job_id}/stream",
    )


@router.get("/analyze/{job_id}/stream")
async def stream_progress(job_id: str):
    """SSE endpoint streaming agent progress events.

    Event types: agent_start, agent_complete, pipeline_done, error.
    """
    job = job_store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return StreamingResponse(
        job_store.subscribe(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/analyze/{job_id}", response_model=JobResult)
async def get_result(job_id: str):
    """Poll for a completed analysis result."""
    job = job_store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResult(
        job_id=job_id,
        status=job.status,
        report=job.final_report,
        error=job.error,
    )


@router.get("/jobs")
async def list_jobs():
    """List recent analysis jobs."""
    return job_store.list_jobs()
