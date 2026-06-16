import os
import time
import logging
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import google.generativeai as genai
import psycopg

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("spiritpulse.embeddings")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "spiritpulse-posts")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

genai.configure(api_key=GEMINI_API_KEY)

def get_embedding(text: str) -> list[float]:
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document",
    )
    return result["embedding"]

def get_posts_from_db() -> list[dict]:
    conn = psycopg.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT post_id, brand_id, brand_name, brand_category,
                   content, sentiment_label, sentiment_score,
                   likes, shares, comments, posted_at
            FROM spiritpulse.social_posts
            ORDER BY posted_at DESC
        """)
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]

def chunk_post(post: dict) -> str:
    return (
        f"Brand: {post['brand_name']} ({post['brand_category']}). "
        f"Sentiment: {post['sentiment_label']} (score: {post['sentiment_score']}). "
        f"Post: {post['content']}"
    )

def run_embedding_pipeline():
    logger.info("Starting embedding pipeline...")

    pc = Pinecone(api_key=PINECONE_API_KEY)

    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        logger.info(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=3072,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        logger.info("Waiting for index to be ready...")
        time.sleep(10)
    else:
        logger.info(f"Index {PINECONE_INDEX_NAME} already exists")

    index = pc.Index(PINECONE_INDEX_NAME)

    logger.info("Fetching posts from Railway Postgres...")
    posts = get_posts_from_db()
    logger.info(f"Found {len(posts)} posts to embed")

    vectors = []
    for i, post in enumerate(posts):
        text = chunk_post(post)

        # Rate limit: 100 requests/min on free tier — pause every 90 requests
        if i > 0 and i % 90 == 0:
            logger.info(f"Rate limit pause: waiting 65 seconds...")
            time.sleep(65)

        try:
            embedding = get_embedding(text)
        except Exception as e:
            if "retry" in str(e).lower() or "quota" in str(e).lower():
                logger.warning(f"Rate limit hit at post {i}, waiting 65 seconds...")
                time.sleep(65)
                embedding = get_embedding(text)
            else:
                raise

        vectors.append({
            "id": post["post_id"],
            "values": embedding,
            "metadata": {
                "brand_id": post["brand_id"],
                "brand_name": post["brand_name"],
                "brand_category": post["brand_category"],
                "sentiment_label": post["sentiment_label"],
                "sentiment_score": float(post["sentiment_score"]),
                "content": post["content"][:500],
                "posted_at": str(post["posted_at"]),
            }
        })

        if (i + 1) % 10 == 0:
            logger.info(f"Embedded {i + 1}/{len(posts)} posts...")

        if len(vectors) == 50:
            index.upsert(vectors=vectors)
            logger.info(f"Upserted batch of 50 vectors")
            vectors = []

    if vectors:
        index.upsert(vectors=vectors)
        logger.info(f"Upserted final batch of {len(vectors)} vectors")

    stats = index.describe_index_stats()
    logger.info(f"Done. Total vectors in index: {stats.total_vector_count}")

if __name__ == "__main__":
    run_embedding_pipeline()