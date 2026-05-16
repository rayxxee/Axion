"""Seed Firestore with demo product data.

Usage: python scripts/seed_firestore.py
Requires FIREBASE_PROJECT_ID and credentials in .env
"""

import json
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from config import settings


def seed():
    """Load seed data and write to Firestore."""
    seed_path = Path(__file__).parent.parent / "backend" / "data" / "seed_pricing.json"
    products = json.loads(seed_path.read_text())
    print(f"Loaded {len(products)} products from seed data")

    if not settings.FIREBASE_PROJECT_ID:
        print("No FIREBASE_PROJECT_ID set. Skipping Firestore write.")
        print("Products that would be seeded:")
        for p in products:
            print(f"  - {p['product_id']}: {p['product_name']} @ PKR {p['base_price_pkr']}")
        return

    import firebase_admin
    from firebase_admin import credentials, firestore

    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred, {"projectId": settings.FIREBASE_PROJECT_ID})
    db = firestore.client()

    batch = db.batch()
    for p in products:
        ref = db.collection("demo_products").document(p["product_id"])
        batch.set(ref, p)

    batch.commit()
    print(f"Seeded {len(products)} products to Firestore")


if __name__ == "__main__":
    seed()
