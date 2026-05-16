"""Firebase Firestore client with CRUD helpers.

Uses firebase-admin SDK. Falls back to a local dict-based mock
when credentials are not configured (hackathon convenience).
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from config import settings

logger = logging.getLogger(__name__)

# Module-level state
_db = None
_mock_mode = False
_mock_store: dict[str, dict[str, Any]] = {
    "pricing_records": {},
    "analysis_jobs": {},
    "demo_products": {},
}


def init_firestore() -> None:
    """Initialize Firestore connection, or fall back to mock mode."""
    global _db, _mock_mode

    cred_path = settings.FIREBASE_CREDENTIALS_PATH
    if not os.path.exists(cred_path) or not settings.FIREBASE_PROJECT_ID:
        logger.warning(
            "Firebase credentials not found or project ID empty. "
            "Running in MOCK Firestore mode."
        )
        _mock_mode = True
        _seed_mock_products()
        return

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            "projectId": settings.FIREBASE_PROJECT_ID,
        })
        _db = firestore.client()
        logger.info("Firestore initialized for project %s", settings.FIREBASE_PROJECT_ID)
    except Exception as exc:
        logger.error("Firestore init failed, falling back to mock: %s", exc)
        _mock_mode = True
        _seed_mock_products()


def _seed_mock_products() -> None:
    """Load seed products into mock store."""
    seed_path = Path(__file__).parent.parent / "data" / "seed_pricing.json"
    if seed_path.exists():
        products = json.loads(seed_path.read_text())
        for p in products:
            _mock_store["demo_products"][p["product_id"]] = p
        logger.info("Seeded %d mock products", len(products))


async def read_demo_products() -> list[dict[str, Any]]:
    """Read all products from the demo_products collection."""
    if _mock_mode:
        return list(_mock_store["demo_products"].values())

    docs = _db.collection("demo_products").stream()
    return [doc.to_dict() for doc in docs]


async def write_pricing_records(
    job_id: str, records: list[dict[str, Any]]
) -> None:
    """Write pricing before/after records to Firestore."""
    if _mock_mode:
        for i, rec in enumerate(records):
            key = f"{job_id}_{i}"
            rec["job_id"] = job_id
            _mock_store["pricing_records"][key] = rec
        logger.info("Mock-wrote %d pricing records for job %s", len(records), job_id)
        return

    batch = _db.batch()
    coll = _db.collection("pricing_records")
    for rec in records:
        rec["job_id"] = job_id
        batch.set(coll.document(), rec)
    batch.commit()
    logger.info("Wrote %d pricing records for job %s", len(records), job_id)


async def save_job(job_id: str, data: dict[str, Any]) -> None:
    """Save or update an analysis job document."""
    if _mock_mode:
        _mock_store["analysis_jobs"][job_id] = data
        return

    _db.collection("analysis_jobs").document(job_id).set(data, merge=True)


async def get_job(job_id: str) -> dict[str, Any] | None:
    """Retrieve an analysis job by ID."""
    if _mock_mode:
        return _mock_store["analysis_jobs"].get(job_id)

    doc = _db.collection("analysis_jobs").document(job_id).get()
    return doc.to_dict() if doc.exists else None


async def get_pricing_records(job_id: str) -> list[dict[str, Any]]:
    """Get all pricing records for a specific job."""
    if _mock_mode:
        return [
            v
            for v in _mock_store["pricing_records"].values()
            if v.get("job_id") == job_id
        ]

    docs = (
        _db.collection("pricing_records")
        .where("job_id", "==", job_id)
        .stream()
    )
    return [doc.to_dict() for doc in docs]
