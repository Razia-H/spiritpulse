from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from api.database import get_db
from api.models import TrendingHashtagOut

router = APIRouter(prefix="/trends", tags=["trends"])

@router.get("", response_model=list[TrendingHashtagOut])
async def get_trending(days: int = Query(default=7, ge=1, le=30), limit: int = Query(default=20, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM spiritpulse_spiritpulse.mart_trending_hashtags WHERE report_date >= current_date - :days * interval '1 day' ORDER BY report_date DESC, trend_rank ASC LIMIT :limit"), {"days": days, "limit": limit})
    rows = result.mappings().all()
    if not rows:
        raise HTTPException(status_code=404, detail="No trend data found.")
    return [TrendingHashtagOut(**row) for row in rows]

@router.get("/{brand_id}", response_model=list[TrendingHashtagOut])
async def get_brand_trends(brand_id: str, days: int = Query(default=7, ge=1, le=30), db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM spiritpulse_spiritpulse.mart_trending_hashtags WHERE brand_id = :brand_id AND report_date >= current_date - :days * interval '1 day' ORDER BY report_date DESC, trend_rank ASC"), {"brand_id": brand_id, "days": days})
    rows = result.mappings().all()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No trend data for brand '{brand_id}'.")
    return [TrendingHashtagOut(**row) for row in rows]
