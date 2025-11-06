from pydantic import BaseModel, Field
from typing import List, Optional

# Each class will map to a collection (lowercased name)

class Variant(BaseModel):
    name: str  # e.g., "128GB", "Blue"
    sku: str
    color: Optional[str] = None
    storage: Optional[str] = None
    price: float
    mrp: float

class EMIPlan(BaseModel):
    tenure_months: int
    monthly_payment: float
    interest_rate: float  # e.g., 0.0 or 10.5
    cashback: Optional[str] = None  # e.g., "₹1000 cashback"
    partner: Optional[str] = None  # e.g., mutual fund partner

class Product(BaseModel):
    slug: str = Field(..., description="URL-friendly unique identifier")
    name: str
    description: Optional[str] = None
    image_url: str
    variants: List[Variant]
    emi_plans: List[EMIPlan]
