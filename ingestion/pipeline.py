import os
import logging
from dotenv import load_dotenv
import dlt
from social_simulator import generate_posts, generate_brands

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("spiritpulse.pipeline")

DATABASE_URL = os.getenv("DATABASE_URL")
SCHEMA = os.getenv("DATABASE_SCHEMA", "spiritpulse")


@dlt.resource(name="social_posts", write_disposition="append", primary_key="post_id")
def social_posts_resource(count: int = 100):
    logger.info(f"Generating {count} social posts...")
    posts = generate_posts(count=count)
    yield posts
    logger.info(f"Yielded {len(posts)} posts to DLT")


@dlt.resource(name="brands", write_disposition="merge", primary_key="brand_id")
def brands_resource():
    brands = generate_brands()
    yield brands
    logger.info(f"Yielded {len(brands)} brands to DLT")


@dlt.source(name="spiritpulse_social")
def spiritpulse_source(post_count: int = 100):
    return [social_posts_resource(count=post_count), brands_resource()]


def run_ingestion(post_count: int = 100) -> None:
    logger.info("=" * 60)
    logger.info("SpiritPulse ingestion starting")
    logger.info(f"Target schema : {SCHEMA}")
    logger.info(f"Post count    : {post_count}")
    logger.info("=" * 60)

    pipeline = dlt.pipeline(
        pipeline_name="spiritpulse",
        destination=dlt.destinations.postgres(DATABASE_URL),
        dataset_name=SCHEMA,
        dev_mode=False,
    )

    source = spiritpulse_source(post_count=post_count)
    load_info = pipeline.run(source)

    logger.info("Ingestion complete")
    logger.info(f"Load IDs: {load_info.loads_ids}")
    logger.info(str(load_info))


if __name__ == "__main__":
    run_ingestion(post_count=200)