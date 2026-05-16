"""Firestore document schemas for type safety."""

from pydantic import BaseModel
from typing import Optional


class PricingRecord(BaseModel):
    """A single pricing record stored in Firestore."""

    job_id: str
    product_id: str
    product_name: str
    category: str
    unit: str
    before_price_pkr: float
    after_price_pkr: float
    change_pct: float
    effective_date: str
    justification: str
    snapshot_type: str  # "before" | "after"


class DemoProduct(BaseModel):
    """A product from the seed catalog."""

    product_id: str
    product_name: str
    category: str
    unit: str
    base_price_pkr: float
    last_updated: str
