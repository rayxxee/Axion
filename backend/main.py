"""PolicyPulse FastAPI application factory."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import analyze, agents
from services.firestore_client import init_firestore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    init_firestore()
    yield


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title="PolicyPulse API",
        description="News-to-Policy Impact Analyzer — 5-agent LLM pipeline",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.include_router(analyze.router)
    app.include_router(agents.router)

    @app.get("/health", tags=["system"])
    async def health():
        return {"status": "ok", "service": "policypulse"}

    return app


app = create_app()
