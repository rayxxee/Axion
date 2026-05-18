import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import os
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from datetime import datetime

# Load .env from project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

if not firebase_admin._apps:
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
    if not os.path.isabs(cred_path):
        cred_path = ROOT_DIR / cred_path
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    except Exception:
        # Fallback for Cloud Run (uses Application Default Credentials)
        firebase_admin.initialize_app()

db = firestore.client()

SEED_PRODUCTS = [
    {
        "id": "PROD-001",
        "name": "Standard Delivery — Lahore",
        "category": "logistics",
        "base_price_pkr": 180,
        "fuel_surcharge_pkr": 63,
        "total_price_pkr": 243,
        "margin_pct": 22.5,
        "last_updated": datetime.utcnow().isoformat(),
        "status": "active"
    },
    {
        "id": "PROD-002",
        "name": "Express Delivery — Karachi",
        "category": "logistics",
        "base_price_pkr": 250,
        "fuel_surcharge_pkr": 87,
        "total_price_pkr": 337,
        "margin_pct": 19.8,
        "last_updated": datetime.utcnow().isoformat(),
        "status": "active"
    },
    {
        "id": "PROD-003",
        "name": "Bulk Freight — Islamabad",
        "category": "freight",
        "base_price_pkr": 850,
        "fuel_surcharge_pkr": 297,
        "total_price_pkr": 1147,
        "margin_pct": 17.2,
        "last_updated": datetime.utcnow().isoformat(),
        "status": "active"
    },
    {
        "id": "PROD-004",
        "name": "Same-Day — Rawalpindi",
        "category": "express",
        "base_price_pkr": 320,
        "fuel_surcharge_pkr": 112,
        "total_price_pkr": 432,
        "margin_pct": 21.0,
        "last_updated": datetime.utcnow().isoformat(),
        "status": "active"
    },
    {
        "id": "PROD-005",
        "name": "Cold Chain — Multan",
        "category": "specialized",
        "base_price_pkr": 560,
        "fuel_surcharge_pkr": 196,
        "total_price_pkr": 756,
        "margin_pct": 14.5,
        "last_updated": datetime.utcnow().isoformat(),
        "status": "active"
    }
]

async def write_pending_analysis(data: dict):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: db.collection("pending_analysis").document(data["run_id"]).set(data)
    )

async def get_pipeline_status():
    loop = asyncio.get_event_loop()
    doc = await loop.run_in_executor(
        None,
        lambda: db.collection("pipeline_status").document("current").get()
    )
    return doc.to_dict() if doc.exists else {"status": "processing"}

async def get_final_report():
    loop = asyncio.get_event_loop()
    doc = await loop.run_in_executor(
        None,
        lambda: db.collection("final_report").document("current").get()
    )
    return doc.to_dict() if doc.exists else None

async def seed_pricing_table():
    loop = asyncio.get_event_loop()
    def _seed():
        for product in SEED_PRODUCTS:
            db.collection("pricing_table").document(product["id"]).set(product)
        # also clear agent outputs for clean run
        for doc_id in ["agent1_result","agent2_result","agent3_result","agent4_result"]:
            db.collection("agent_outputs").document(doc_id).set({"status": "pending"})
        db.collection("pipeline_status").document("current").set({"status": "idle"})
    await loop.run_in_executor(None, _seed)

async def get_analysis_history():
    loop = asyncio.get_event_loop()
    def _fetch():
        docs = (
            db.collection("pending_analysis")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(20)
            .stream()
        )
        return [doc.to_dict() for doc in docs]
    return await loop.run_in_executor(None, _fetch)

async def get_execution_log():
    loop = asyncio.get_event_loop()
    def _fetch():
        docs = db.collection("execution_log").order_by("timestamp").stream()
        return [doc.to_dict() for doc in docs]
    return await loop.run_in_executor(None, _fetch)
