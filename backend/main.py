from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.firebase_client import (
    write_pending_analysis,
    seed_pricing_table,
    get_pipeline_status,
    get_final_report
)
from services.news_ingester import fetch_article_from_url
import uuid
from datetime import datetime

app = FastAPI(title="Axion API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    input_type: str   # "text" | "url" | "demo"
    content: str      # raw text or URL

DEMO_INPUT = """SBP has raised the policy rate by 200 basis points to 22%,
effective immediately. This is the third consecutive hike aimed at controlling
inflation which stands at 28% YoY."""

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0", "architecture": "antigravity-orchestrated"}

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Receives article from Flutter.
    Writes it to Firestore pending_analysis.
    Antigravity agents take over from here.
    """
    run_id = str(uuid.uuid4())

    if request.input_type == "demo":
        article_text = DEMO_INPUT
    elif request.input_type == "url":
        article_text = await fetch_article_from_url(request.content)
        if not article_text:
            raise HTTPException(status_code=400, detail="Could not fetch article from URL")
    else:
        article_text = request.content

    if len(article_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Article text too short")

    await write_pending_analysis({
        "run_id": run_id,
        "article_text": article_text,
        "input_type": request.input_type,
        "created_at": datetime.utcnow().isoformat(),
        "status": "pending"
    })

    return {
        "run_id": run_id,
        "status": "queued",
        "message": "Article queued. Antigravity agents are processing."
    }

@app.get("/status/{run_id}")
async def check_status(run_id: str):
    """Flutter polls this until status is complete."""
    status = await get_pipeline_status()
    return status

@app.get("/report")
async def get_report():
    """Flutter reads final report after pipeline_status is complete."""
    report = await get_final_report()
    if not report:
        raise HTTPException(status_code=404, detail="No report available yet")
    return report

@app.post("/seed")
async def seed():
    """Seeds Firestore pricing_table with before-state data."""
    await seed_pricing_table()
    return {"status": "seeded", "message": "Pricing table restored to baseline"}
