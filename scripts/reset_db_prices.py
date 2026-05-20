import asyncio
import sys
import os
sys.path.append(os.path.abspath('.'))
from backend.services.firebase_client import db

async def reset_prices():
    prices = {
        "PROD-001": 250,
        "PROD-002": 300,
        "PROD-003": 950,
        "PROD-004": 350,
        "PROD-005": 600
    }
    for doc_id, price in prices.items():
        doc_ref = db.collection("pricing_table").document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update({"total_price_pkr": price})
            print(f"Updated {doc_id} total_price_pkr to {price}")
        else:
            print(f"{doc_id} not found")

if __name__ == "__main__":
    asyncio.run(reset_prices())
