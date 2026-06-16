"""
routers/search.py
GET /search?q=your+query
Semantic search over social posts using Pinecone + Gemini embeddings.
"""

import os
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from pinecone import Pinecone
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/search", tags=["semantic search"])

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "spiritpulse-posts")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

class SearchResult(BaseModel):
    post_id: str
    brand_name: str
    brand_category: str
    sentiment_label: str
    sentiment_score: float
    content: str
    posted_at: str
    similarity_score: float

def get_query_embedding(query: str) -> list[float]:
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=query,
        task_type="retrieval_query",
    )
    return result["embedding"]

@router.get("", response_model=list[SearchResult])
async def semantic_search(
    q: str = Query(..., description="Natural language search query"),
    top_k: int = Query(default=5, ge=1, le=20),
    brand_id: str = Query(default=None, description="Filter by brand ID"),
    sentiment: str = Query(default=None, description="Filter by sentiment: positive, negative, neutral"),
):
    """
    Semantic search over social posts using vector embeddings.
    Example: /search?q=customers complaining about price
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)

        query_vector = get_query_embedding(q)

        filter_dict = {}
        if brand_id:
            filter_dict["brand_id"] = {"$eq": brand_id}
        if sentiment:
            filter_dict["sentiment_label"] = {"$eq": sentiment}

        results = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict if filter_dict else None,
        )

        if not results.matches:
            raise HTTPException(status_code=404, detail="No matching posts found.")

        return [
            SearchResult(
                post_id=match.id,
                brand_name=match.metadata.get("brand_name", ""),
                brand_category=match.metadata.get("brand_category", ""),
                sentiment_label=match.metadata.get("sentiment_label", ""),
                sentiment_score=match.metadata.get("sentiment_score", 0.0),
                content=match.metadata.get("content", ""),
                posted_at=match.metadata.get("posted_at", ""),
                similarity_score=round(match.score, 4),
            )
            for match in results.matches
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")