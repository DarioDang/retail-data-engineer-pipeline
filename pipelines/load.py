"""Load pipeline: reads Parquet files from S3 and loads into Postgres"""

import os 
import dlt 
import boto3 
import logging 
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ── Setup ─────────────────────────────────────────────────────────────────────
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION  = os.getenv("AWS_REGION")

# ── Postgres Connection ────────────────────────────────────────────────────────
def get_postgres_engine():
    return create_engine(
        f"postgresql://"
        f"{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )

# ── Check if Date Already Loaded ───────────────────────────────────────────────
def is_date_already_loaded(date: str) -> bool:
    """Check if data for this date already exists in Postgres."""
    try:
        engine = get_postgres_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM raw_shopping.electronic_products
                WHERE DATE(ingested_at AT TIME ZONE 'Pacific/Auckland') = :date
                   OR DATE(ingested_at) = :date
            """), {"date": date})
            count = result.scalar()
            if count > 0:
                logger.info(f"Data for {date} already exists ({count} records) — skipping load")
                return True
            return False
    except Exception as e:
        logger.warning(f"Could not check existing data: {e} — proceeding with load")
        return False

# ── List Available Dates in S3 ─────────────────────────────────────────────────
def list_available_dates() -> list[str]:
    """List all available date partitions in S3."""
    try:
        s3 = boto3.client("s3", region_name=AWS_REGION)
        response = s3.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix="raw/shopping/",
            Delimiter="/"
        )
        dates = [
            p["Prefix"].split("/")[2]
            for p in response.get("CommonPrefixes", [])
        ]
        logger.info(f"Available dates in S3: {dates}")
        return sorted(dates)
    except Exception as e:
        logger.error(f"Failed to list dates from S3: {e}")
        return []

# ── Read Parquet from S3 ───────────────────────────────────────────────────────
def read_parquet_from_s3(date: str) -> list[dict]:
    """Read Parquet files from S3 for a given date partition."""
    try:
        s3 = boto3.client("s3", region_name=AWS_REGION)
        prefix = f"raw/shopping/{date}/shopping_results/"
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

        parquet_files = [
            f"s3://{BUCKET_NAME}/{obj['Key']}"
            for obj in response.get("Contents", [])
            if obj["Key"].endswith(".parquet")
        ]

        if not parquet_files:
            logger.warning(f"No Parquet files found for date: {date}")
            return []

        logger.info(f"Found {len(parquet_files)} Parquet files for date: {date}")

        dfs = [
            pd.read_parquet(f, storage_options={"anon": False})
            for f in parquet_files
        ]
        df = pd.concat(dfs, ignore_index=True)
        logger.info(f"Read {len(df)} records from S3 for date: {date}")
        return df.to_dict(orient="records")

    except Exception as e:
        logger.error(f"Failed to read from S3 for date '{date}': {e}")
        return []

# ── dlt Resource ───────────────────────────────────────────────────────────────
@dlt.resource(
    name="electronic_products",
    write_disposition="append",         # ← keep append
    columns={"old_price": {"data_type": "double"}}
)
def shopping_resource(date: str):
    """dlt resource that yields records from S3 Parquet files."""
    records = read_parquet_from_s3(date)
    if not records:
        logger.warning(f"No records found for date: {date}")
        return
    for record in records:
        yield record

# ── Pipeline ───────────────────────────────────────────────────────────────────
def run_load(date: str = None):
    """Load data from S3 into Postgres for a given date."""

    # Auto-detect latest available date in S3 if not provided
    if date is None:
        available_dates = list_available_dates()
        if not available_dates:
            logger.error("No data found in S3 — run ingest.py first")
            return
        date = available_dates[-1]
        logger.info(f"Auto-selected latest date: {date}")

    # ── Skip if already loaded ─────────────────────────────────────────────────
    if is_date_already_loaded(date):
        logger.info(f"Skipping — {date} already loaded into Postgres")
        return

    logger.info(f"Loading data for date: {date}")

    pipeline = dlt.pipeline(
        pipeline_name="retail_price_intelligence_load",
        destination=dlt.destinations.postgres(
            credentials=(
                f"postgresql://"
                f"{os.getenv('POSTGRES_USER')}:"
                f"{os.getenv('POSTGRES_PASSWORD')}@"
                f"{os.getenv('POSTGRES_HOST')}:"
                f"{os.getenv('POSTGRES_PORT')}/"
                f"{os.getenv('POSTGRES_DB')}"
            )
        ),
        dataset_name="raw_shopping"
    )

    load_info = pipeline.run(shopping_resource(date=date))
    logger.info(f"Load complete: {load_info}")
    return load_info

# ── Backfill ───────────────────────────────────────────────────────────────────
def run_backfill():
    """Load all available dates from S3 that haven't been loaded yet."""
    available_dates = list_available_dates()
    
    if not available_dates:
        logger.error("No data found in S3 — run ingest.py first")
        return

    logger.info(f"Found {len(available_dates)} dates to check: {available_dates}")

    for date in available_dates:
        if is_date_already_loaded(date):
            logger.info(f"Skipping {date} — already loaded")
            continue
        logger.info(f"Loading missing date: {date}")
        run_load(date=date)

# Main 
if __name__ == "__main__":
    run_load()