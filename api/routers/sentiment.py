from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from api.database import get_db
from api.models import BrandSentimentOut, SentimentSummaryOut

router = APIRouter(prefix="/sentiment", tags=["sentiment"])

@router.get("", response_model=list[BrandSentimentOut])
async def get_all_sentiment(days: int = Query(default=7, ge=1, le=90), db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM spiritpulse_spiritpulse.mart_brand_sentiment WHERE report_date >= current_date - :days * interval '1 day' ORDER BY report_date DESC, daily_sentiment_rank ASC"), {"days": days})
    rows = result.mappings().all()
    if not rows:
        raise HTTPException(status_code=404, detail="No sentiment data found. Run ingestion then dbt.")
    return [BrandSentimentOut(**row) for row in rows]

@router.get("/{brand_id}/summary", response_model=SentimentSummaryOut)
async def get_brand_summary(brand_id: str, days: int = Query(default=30, ge=1, le=90), db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT brand_id, brand_name, brand_category,
               round(avg(avg_sentiment_score)::numeric, 3) as avg_sentiment_score,
               CASE WHEN avg(avg_sentiment_score) >= 0.65 THEN 'bullish' WHEN avg(avg_sentiment_score) >= 0.45 THEN 'neutral' ELSE 'bearish' END as sentiment_signal,
               sum(total_posts) as total_posts,
               round(avg(positive_pct)::numeric, 1) as positive_pct,
               round(avg(negative_pct)::numeric, 1) as negative_pct,
               sum(total_engagement) as total_engagement,
               count(distinct report_date) as days_analyzed
        FROM spiritpulse_spiritpulse.mart_brand_sentiment
        WHERE brand_id = :brand_id AND report_date >= current_date - :days * interval '1 day'
        GROUP BY brand_id, brand_name, brand_category
    """), {"brand_id": brand_id, "days": days})
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail=f"No data for brand '{brand_id}'.")
    return SentimentSummaryOut(**row)

@router.get("/{brand_id}", response_model=list[BrandSentimentOut])
async def get_brand_sentiment(brand_id: str, days: int = Query(default=7, ge=1, le=90), db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM spiritpulse_spiritpulse.mart_brand_sentiment WHERE brand_id = :brand_id AND report_date >= current_date - :days * interval '1 day' ORDER BY report_date DESC"), {"brand_id": brand_id, "days": days})
    rows = result.mappings().all()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No sentiment data for brand '{brand_id}'.")
    return [BrandSentimentOut(**row) for row in rows]
