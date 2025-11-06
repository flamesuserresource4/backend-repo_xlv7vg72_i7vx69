from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import get_db, create_document, get_documents, get_one
from schemas import Product, Variant, EMIPlan

app = FastAPI(title="Products API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

@app.get("/", response_model=Message)
async def root():
    return Message(message="Backend is running")

@app.get("/test")
async def test_db():
    db = await get_db()
    names = await db.list_collection_names()
    return {
        "backend": "ok",
        "database": "mongodb",
        "database_url": "env",
        "database_name": db.name,
        "connection_status": "connected",
        "collections": names,
    }

# Seed demo data if empty
async def seed_if_empty():
    db = await get_db()
    if await db["product"].count_documents({}) == 0:
        demo_products: List[Product] = [
            Product(
                slug="iphone-17-pro",
                name="iPhone 17 Pro",
                description="The ultimate iPhone experience.",
                image_url="https://images.unsplash.com/photo-1661961112951-f2bfd1f253ce?q=80&w=1200&auto=format&fit=crop",
                variants=[
                    Variant(name="128GB", sku="IP17P-128-SIL", color="Silver", storage="128GB", mrp=139999, price=129999),
                    Variant(name="256GB", sku="IP17P-256-BLK", color="Black", storage="256GB", mrp=149999, price=139999),
                ],
                emi_plans=[
                    EMIPlan(tenure_months=3, monthly_payment=44999.67, interest_rate=0.0, cashback="₹1000 via MF partner", partner="BlueFund"),
                    EMIPlan(tenure_months=6, monthly_payment=23666.50, interest_rate=10.5, cashback=None, partner="BlueFund"),
                    EMIPlan(tenure_months=9, monthly_payment=16222.11, interest_rate=12.5, cashback=None, partner="GreenInvest"),
                ],
            ),
            Product(
                slug="samsung-s24-ultra",
                name="Samsung S24 Ultra",
                description="Epic camera and performance.",
                image_url="https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?q=80&w=1200&auto=format&fit=crop",
                variants=[
                    Variant(name="256GB", sku="SS24U-256-GRY", color="Gray", storage="256GB", mrp=129999, price=119999),
                    Variant(name="512GB", sku="SS24U-512-PUR", color="Purple", storage="512GB", mrp=149999, price=134999),
                ],
                emi_plans=[
                    EMIPlan(tenure_months=3, monthly_payment=39999.67, interest_rate=0.0, cashback="₹1500 via MF partner", partner="BlueFund"),
                    EMIPlan(tenure_months=6, monthly_payment=20666.50, interest_rate=9.5, cashback=None, partner="AlphaGrowth"),
                ],
            ),
            Product(
                slug="oneplus-12",
                name="OnePlus 12",
                description="Fast and smooth performance.",
                image_url="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=1200&auto=format&fit=crop",
                variants=[
                    Variant(name="128GB", sku="OP12-128-GRN", color="Green", storage="128GB", mrp=69999, price=64999),
                    Variant(name="256GB", sku="OP12-256-BLK", color="Black", storage="256GB", mrp=79999, price=72999),
                ],
                emi_plans=[
                    EMIPlan(tenure_months=3, monthly_payment=21666.33, interest_rate=0.0, cashback=None, partner="AlphaGrowth"),
                    EMIPlan(tenure_months=6, monthly_payment=11222.50, interest_rate=8.0, cashback="₹500", partner="GreenInvest"),
                ],
            ),
        ]
        for p in demo_products:
            await create_document("product", p.model_dump())

@app.on_event("startup")
async def on_startup():
    await seed_if_empty()

# API Endpoints
@app.get("/api/products")
async def list_products():
    await seed_if_empty()
    products = await get_documents("product")
    return products

@app.get("/api/products/{slug}")
async def get_product(slug: str):
    await seed_if_empty()
    product = await get_one("product", {"slug": slug})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
