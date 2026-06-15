"""
models.py
Pydantic response models for all FastAPI endpoints.
These define exactly what the API returns — no raw DB rows exposed.
"""

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class BrandOut(BaseModel):
    brand_id: str
    brand_name: str
    category: str
    primary_hashtag: str

    model_config = {"from_attributes": True}


class BrandSentimentOut(BaseModel):
    brand_id: str
    brand_name: str
    brand_category: str
    report_date: date
    total_posts: int
    positive_count: int
    negative_count: int
    neutral_count: int
    avg_sentiment_score: float = Field(..., ge=0.0, le=1.0)
    positive_pct: float
    negative_pct: float
    total_engagement: int
    avg_engagement: float
    total_likes: int
    total_shares: int
    total_comments: int
    sentiment_signal: str = Field(..., description="bullish | neutral | bearish")
    daily_sentiment_rank: int
    last_ingested_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TrendingHashtagOut(BaseModel):
    hashtag: str
    brand_id: str
    brand_name: str
    brand_category: str
    report_date: date
    mention_count: int
    avg_sentiment: float
    total_engagement: int
    positive_mentions: int
    negative_mentions: int
    trend_rank: int

    model_config = {"from_attributes": True}


class SentimentSummaryOut(BaseModel):
    brand_id: str
    brand_name: str
    brand_category: str
    avg_sentiment_score: float
    sentiment_signal: str
    total_posts: int
    positive_pct: float
    negative_pct: float
    total_engagement: int
    days_analyzed: int


class HealthOut(BaseModel):
    status: str
    database: str
    schema_: str = Field(..., alias="schema")
    version: str = "1.0.0"
