"""In-memory job state store with async SSE subscription."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncGenerator

logger = logging.getLogger(__name__)


@dataclass
class JobState:
    """Tracks the state of a single analysis pipeline run."""

    job_id: str
    status: str = "processing"  # processing | completed | failed
    events: list[dict[str, Any]] = field(default_factory=list)
    agent_outputs: dict[str, Any] = field(default_factory=dict)
    final_report: dict[str, Any] | None = None
    error: str | None = None
    _subscribers: list[asyncio.Queue] = field(default_factory=list)


# Global store
_jobs: dict[str, JobState] = {}


def create_job(job_id: str) -> JobState:
    """Create a new job entry."""
    job = JobState(job_id=job_id)
    _jobs[job_id] = job
    logger.info("Job created: %s", job_id)
    return job


def get_job(job_id: str) -> JobState | None:
    """Retrieve job state by ID."""
    return _jobs.get(job_id)


async def update_job(
    job_id: str,
    event_type: str,
    agent: str = "",
    data: dict[str, Any] | None = None,
) -> None:
    """Push an event to the job and notify all SSE subscribers."""
    job = _jobs.get(job_id)
    if job is None:
        return

    event = {
        "event": event_type,
        "agent": agent,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data or {},
    }
    job.events.append(event)

    # Store agent output if this is a completion event
    if event_type == "agent_complete" and agent and data:
        job.agent_outputs[agent] = data

    if event_type == "pipeline_done":
        job.status = "completed"
        job.final_report = data

    if event_type == "error":
        job.status = "failed"
        job.error = data.get("message", "Unknown error") if data else "Unknown error"

    # Notify SSE subscribers
    sse_line = f"data: {json.dumps(event)}\n\n"
    for queue in job._subscribers:
        await queue.put(sse_line)

    # Close subscriber queues on terminal events
    if event_type in ("pipeline_done", "error"):
        for queue in job._subscribers:
            await queue.put(None)  # sentinel
        job._subscribers.clear()


async def subscribe(job_id: str) -> AsyncGenerator[str, None]:
    """Async generator yielding SSE events for a job.

    Yields formatted SSE data lines. Stops on pipeline_done or error.
    """
    job = _jobs.get(job_id)
    if job is None:
        yield f"data: {json.dumps({'event': 'error', 'data': {'message': 'Job not found'}})}\n\n"
        return

    # Replay existing events
    for event in job.events:
        yield f"data: {json.dumps(event)}\n\n"

    # If job already terminal, stop
    if job.status in ("completed", "failed"):
        return

    # Subscribe to new events
    queue: asyncio.Queue[str | None] = asyncio.Queue()
    job._subscribers.append(queue)

    try:
        while True:
            item = await queue.get()
            if item is None:
                break
            yield item
    finally:
        if queue in job._subscribers:
            job._subscribers.remove(queue)


def list_jobs(limit: int = 50) -> list[dict[str, Any]]:
    """Return recent jobs as summary dicts."""
    jobs = sorted(
        _jobs.values(),
        key=lambda j: j.events[0]["timestamp"] if j.events else "",
        reverse=True,
    )[:limit]

    return [
        {
            "job_id": j.job_id,
            "status": j.status,
            "event_count": len(j.events),
            "headline": (
                j.agent_outputs.get("news_parser", {}).get("headline", "")
                if j.agent_outputs
                else ""
            ),
        }
        for j in jobs
    ]
