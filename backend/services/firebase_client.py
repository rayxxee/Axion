import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime

load_dotenv()

if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
    firebase_admin.initialize_app(cred)

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
