from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from api.database import get_db
from api.models import BrandOut

router = APIRouter(prefix="/brands", tags=["brands"])

@router.get("", response_model=list[BrandOut])
async def list_brands(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT brand_id, brand_name, category, primary_hashtag FROM spiritpulse.brands ORDER BY brand_name"))
    rows = result.mappings().all()
    if not rows:
        raise HTTPException(status_code=404, detail="No brands found. Run the ingestion pipeline first.")
    return [BrandOut(**row) for row in rows]

@router.get("/{brand_id}", response_model=BrandOut)
async def get_brand(brand_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT brand_id, brand_name, category, primary_hashtag FROM spiritpulse.brands WHERE brand_id = :brand_id"), {"brand_id": brand_id})
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found.")
    return BrandOut(**row)
