import os
import subprocess
from pathlib import Path
from prefect import flow, task, get_run_logger
from prefect.blocks.system import Secret
from sqlalchemy import create_engine, text
from prefect.client.schemas.schedules import CronSchedule
from prefect_aws import AwsCredentials

# ── Base paths ─────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent.parent
PIPELINES_DIR = BASE_DIR / "pipelines"
DBT_DIR      = BASE_DIR / "dbt" / "retail_pipeline"

# ── Load secrets from Prefect Blocks ──────────────────────────────────────────
def load_env_from_blocks():
    """Load all secrets from Prefect Cloud blocks into environment variables."""
    # AWS Credentials block
    aws_creds = AwsCredentials.load("retail-aws-credentials")
    os.environ["AWS_ACCESS_KEY_ID"]     = aws_creds.aws_access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = aws_creds.aws_secret_access_key.get_secret_value()
    os.environ["AWS_REGION"]            = aws_creds.region_name
    os.environ["AWS_BUCKET_NAME"]       = "dario-retail-price-pipeline"

    # SerpAPI key
    os.environ["SERPAPI_KEY"] = Secret.load("serpapi-key").get()

    # Postgres — host/user/db/port are not sensitive, password from block
    os.environ["POSTGRES_HOST"]     = "ep-proud-queen-a7aoci50.ap-southeast-2.aws.neon.tech"
    os.environ["POSTGRES_USER"]     = "neondb_owner"
    os.environ["POSTGRES_PASSWORD"] = Secret.load("postgres-password").get()
    os.environ["POSTGRES_DB"]       = "neondb"
    os.environ["POSTGRES_PORT"]     = "5432"

# ── Tasks ──────────────────────────────────────────────────────────────────────
@task(name="Ingest: SerpAPI → S3", retries=2, retry_delay_seconds=30)
def ingest_task():
    logger = get_run_logger()
    logger.info("Starting ingestion from SerpAPI → S3...")
    result = subprocess.run(
        ["python", str(PIPELINES_DIR / "ingest.py")],
        capture_output=True, text=True,
        cwd=str(PIPELINES_DIR),
        env=os.environ.copy()
    )
    if result.stdout: logger.info(result.stdout)
    if result.stderr: logger.warning(result.stderr)
    if result.returncode != 0:
        raise Exception(f"Ingest failed: {result.stderr}")
    logger.info("✅ Ingest complete")

@task(name="Load: S3 → Postgres", retries=2, retry_delay_seconds=30)
def load_task():
    logger = get_run_logger()
    logger.info("Starting load from S3 → Postgres...")
    result = subprocess.run(
        ["python", str(PIPELINES_DIR / "load.py")],
        capture_output=True, text=True,
        cwd=str(PIPELINES_DIR),
        env=os.environ.copy()
    )
    if result.stdout: logger.info(result.stdout)
    if result.stderr: logger.warning(result.stderr)
    if result.returncode != 0:
        raise Exception(f"Load failed: {result.stderr}")
    logger.info("✅ Load complete")

@task(name="dbt: Run Models", retries=1, retry_delay_seconds=60)
def dbt_run_task():
    logger = get_run_logger()
    logger.info("Running dbt models...")
    result = subprocess.run(
        ["dbt", "run", "--profiles-dir", ".", "--target", "cloud"],
        capture_output=True, text=True,
        cwd=str(DBT_DIR),
        env=os.environ.copy()
    )
    if result.stdout: logger.info(result.stdout)
    if result.stderr: logger.warning(result.stderr)
    if result.returncode != 0:
        raise Exception(f"dbt run failed: {result.stderr}")
    logger.info("✅ dbt run complete")

@task(name="dbt: Test Models", retries=1, retry_delay_seconds=60)
def dbt_test_task():
    logger = get_run_logger()
    logger.info("Running dbt tests...")
    result = subprocess.run(
        ["dbt", "test", "--profiles-dir", ".", "--target", "cloud"],
        capture_output=True, text=True,
        cwd=str(DBT_DIR),
        env=os.environ.copy()
    )
    if result.stdout: logger.info(result.stdout)
    if result.stderr: logger.warning(result.stderr)
    if result.returncode != 0:
        raise Exception(f"dbt test failed: {result.stderr}")
    logger.info("✅ dbt tests passed")

@task(name="Cleanup: Remove old records", retries=1, retry_delay_seconds=30)
def cleanup_task():
    logger = get_run_logger()
    logger.info("Running 90-day retention cleanup...")

    engine = create_engine(
        f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
        f"@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}"
        f"/{os.environ['POSTGRES_DB']}"
    )

    with engine.connect() as conn:
        result = conn.execute(text("""
            DELETE FROM raw_shopping.electronic_products
            WHERE ingested_at < NOW() - INTERVAL '90 days'
        """))
        conn.commit()
        logger.info(f"Deleted {result.rowcount} rows older than 90 days")

    engine.dispose()
    logger.info("Cleanup complete")

@task(name="ML: Train Prophet Models", retries = 1, retry_delay_seconds=60)
def ml_train_task():
    """
    train Prophet models for each product-seller series and save them to s3
    """
    logger = get_run_logger()
    logger.info("Runing Prophet training...")
    result = subprocess.run(
        ["python", str(BASE_DIR / "ml" / "train.py")],
        capture_output =True, text=True,
        cwd=str(BASE_DIR),
        env = os.environ.copy()
    )

    if result.stdout:logger.info(result.stdout)
    if result.stderr: logger.warning(result.stderr)
    if result.returncode !=0:
        raise Exception(f"ML training failed: {result.stderr}")
    logger.info("✅ ML training complete")

@task(name="ML: Generate Forecasts", retries=1, retry_delay_seconds=60)
def ml_predict_task():
    logger = get_run_logger()
    logger.info("Running Prophet forecasting...")
    result = subprocess.run(
        ["python", str(BASE_DIR / "ml" / "predict.py")],
        capture_output=True, text=True,
        cwd=str(BASE_DIR),
        env=os.environ.copy()
    )
    if result.stdout: logger.info(result.stdout)
    if result.stderr: logger.warning(result.stderr)
    if result.returncode != 0:
        raise Exception(f"ML forecasting failed: {result.stderr}")
    logger.info("✅ ML forecasting complete")

# ── Main Flow ──────────────────────────────────────────────────────────────────
@flow(
    name="retail-price-pipeline",
    description="Daily retail price intelligence: SerpAPI → S3 → Postgres → dbt → ML forecasts"
)
def retail_pipeline():
    from datetime import datetime
    import pytz

    logger = get_run_logger()
    logger.info("🚀 Starting Retail Price Pipeline...")

    # Load all secrets first
    load_env_from_blocks()

    # Daily tasks — always run
    ingest_task()
    load_task()
    cleanup_task()
    dbt_run_task()
    dbt_test_task()

    # ML predict — runs daily after dbt
    ml_predict_task()

    # ML train — runs weekly on Sunday (NZT)
    nzt = pytz.timezone('Pacific/Auckland')
    today_nzt = datetime.now(nzt)
    is_sunday = today_nzt.weekday() == 6  

    if is_sunday:
        logger.info("Sunday — running weekly model retraining...")
        ml_train_task()
    else:
        logger.info(f"Not Sunday (weekday={today_nzt.weekday()}) — skipping retraining")

    logger.info("🎉 Pipeline completed successfully!")

if __name__ == "__main__":
    retail_pipeline.from_source(
        source="https://github.com/DarioDang/retail-data-engineer-pipeline.git",
        entrypoint="pipelines/pipeline_flow.py:retail_pipeline",
    ).deploy(
        name="retail-daily-pipeline",
        work_pool_name="retail-managed-pool",
        schedules=[
            CronSchedule(
                cron="0 20 * * *",
                timezone="Pacific/Auckland"
            )
        ],
        job_variables={
            "pip_packages": [
            "prefect-aws",
            "dlt[parquet]",
            "dlt[filesystem]",
            "dlt[postgres]",
            "serpapi",
            "boto3",
            "pandas",
            "pyarrow",
            "sqlalchemy",
            "psycopg2-binary",
            "python-dotenv",
            "pytz",
            "dbt-core",
            "dbt-postgres",
            "prophet",          
            "cmdstanpy",        
            ]
        }
    )
