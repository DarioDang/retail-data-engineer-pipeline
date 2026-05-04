"""
Python script to automatically scrape data using SerpAPI and ingest it directly into S3 bucket
"""

import os 
import dlt
import serpapi
import logging
import boto3
from datetime import datetime, timezone
from dotenv import load_dotenv
import json
from pathlib import Path
import pytz

# ── Setup ─────────────────────────────────────────────────────────────────────
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

SERPAPI_KEY  = os.getenv("SERPAPI_KEY")
COUNTRY_CODE = "nz"
NUM_RESULTS  = 40  # int not string

# ── Serpapi ───────────────────────────────────────────────────────────────────
client = serpapi.Client(api_key=SERPAPI_KEY)

# ── Product Basket ─────────────────────────────────────────────────────────────
PRODUCTS = [
    {"name": "Dell XPS 13",        "query": "Dell XPS 13 laptop",          "category": "laptop"},
    {"name": "MacBook Air M3",      "query": "Apple MacBook Air M3",         "category": "laptop"},
    {"name": "HP Spectre x360",     "query": "HP Spectre x360 laptop",       "category": "laptop"},
    {"name": "iPhone 15",           "query": "Apple iPhone 15 smartphone",   "category": "phone"},
    {"name": "Samsung Galaxy S24",  "query": "Samsung Galaxy S24 phone",     "category": "phone"},
    {"name": "Samsung Galaxy A54",  "query": "Samsung Galaxy A54 phone",     "category": "phone"},
    {"name": "GoPro Hero 13",       "query": "GoPro Hero 13 action camera",  "category": "camera"},
    {"name": "DJI Osmo Action",     "query": "DJI Osmo Action camera",       "category": "camera"},
]

# ── Fetch ──────────────────────────────────────────────────────────────────────
CACHE_DIR = Path("/pipelines/.cache") 
USE_CACHE = os.getenv("USE_CACHE", "true").lower() == "true"

def fetch_product(query: str, num_results: int = NUM_RESULTS) -> list[dict]:
    """Fetch with date-based cache to avoid wasting API calls."""

    # Use NZ timezone for cache dating
    nz_tz = pytz.timezone("Pacific/Auckland")
    today = datetime.now(nz_tz).strftime("%Y-%m-%d")

    # Check cache first — cache is date specific
    if USE_CACHE:
        cache_file = CACHE_DIR / today / f"{query.replace(' ', '_')}.json"
        if cache_file.exists():
            logger.info(f"Cache hit [{today}]: {query}")
            with open(cache_file) as f:
                return json.load(f)

    # Real API call
    try:
        results = client.search({
            "engine": "google_shopping",
            "q":      query,
            "gl":     COUNTRY_CODE,
            "hl":     "en"
        })
        shopping = results.get("shopping_results", [])[:num_results]
        logger.info(f"Fetched {len(shopping)} results for: {query}")

        # Save to date-based cache
        if USE_CACHE:
            cache_date_dir = CACHE_DIR / today
            cache_date_dir.mkdir(parents=True, exist_ok=True)
            cache_file = cache_date_dir / f"{query.replace(' ', '_')}.json"
            with open(cache_file, "w") as f:
                json.dump(shopping, f)

        return shopping

    except Exception as e:
        logger.error(f"Failed to fetch '{query}': {e}")
        return []

# ── Parse ──────────────────────────────────────────────────────────────────────
def parse_product(result: dict, category: str, product_name: str) -> dict:
    """Extract and normalize fields from a raw SerpAPI shopping result."""
    return {
        "product_name": product_name,
        "category":     category,
        "title":        result.get("title"),
        "price":        result.get("extracted_price"),
        "old_price":    float(result["extracted_old_price"]) if result.get("extracted_old_price") else None,
        "seller":       result.get("source"),
        "rating":       float(result["rating"]) if result.get("rating") else None,
        "reviews":      int(result["reviews"]) if result.get("reviews") else None,
        "position":     int(result["position"]) if result.get("position") else None,
        "ingested_at":  datetime.now(timezone.utc).isoformat(),
    }

# ── dlt Resource ───────────────────────────────────────────────────────────────
@dlt.resource(
    name="electronic_products",
    write_disposition="append",
    columns={"old_price": {"data_type": "double"}}
)
def shopping_resource():
    """dlt resource that yields parsed records for all products."""
    for product in PRODUCTS:
        logger.info(f"Processing: {product['name']}")
        raw_results = fetch_product(product["query"])
        for result in raw_results:
            yield parse_product(result, product["category"], product["name"])

def is_date_already_ingested(date: str) -> bool:
    """Check if parquet files already exist in s3 for this date."""
    try:
        s3 = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        prefix = f"raw/shopping/{date}/shopping_results/"
        response = s3.list_objects_v2(
            Bucket=os.getenv("AWS_BUCKET_NAME"),
            Prefix=prefix
        )
        parquet_files = [
            obj for obj in response.get("Contents", [])
            if obj["Key"].endswith(".parquet")
        ]
        if parquet_files:
            logger.info(f"Data for {date} already exists in S3 ({len(parquet_files)} files) — skipping ingest")
            return True
        return False
    except Exception as e:
        logger.warning(f"Could not check S3: {e} — proceeding with ingest")
        return False

# ── Pipeline ───────────────────────────────────────────────────────────────────
def run_ingest():
    """Build and run the dlt pipeline to S3."""
    nz_tz = pytz.timezone("Pacific/Auckland")
    today = datetime.now(nz_tz).strftime("%Y-%m-%d")

    # Skip if already ingested
    if is_date_already_ingested(today):
        logger.info(f"Skipping ingest — data for {today} already in S3")
        return

    bucket_url = (
        f"s3://{os.getenv('AWS_BUCKET_NAME')}"
        f"/raw/shopping/{today}"
    )

    pipeline = dlt.pipeline(
        pipeline_name="retail_price_intelligence",
        destination=dlt.destinations.filesystem(
            bucket_url=bucket_url,
            credentials={
                "region_name":           os.getenv("AWS_REGION"),
                "aws_access_key_id":     os.getenv("AWS_ACCESS_KEY_ID"),
                "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            }
        ),
        dataset_name="shopping_results"
    )

    # Force Parquet format
    pipeline.run(
        shopping_resource(),
        loader_file_format="parquet"
    )

    logger.info(f"Ingestion complete for date: {today}")
    logger.info(f"Data stored at: {bucket_url}")

if __name__ == "__main__":
    run_ingest()