# ml/train.py
# Production training script — trains one Prophet model per series,
# saves each model to S3 (s3://dario-retail-price-pipeline/ml/models/)
# and caches locally to ml/models/ for faster subsequent local runs.
#
# Usage:
#   cd ~/Desktop/Project/retail-data-engineer-pipeline
#   loadenv
#   pipenv run python ml/train.py
#
# Safe to re-run — overwrites existing models in S3 and local cache.

import os
import sys
import pickle
import logging
import boto3
import pandas as pd
from io import BytesIO
from pathlib import Path
from datetime import datetime
from prophet import Prophet
from sqlalchemy import create_engine, text

# ── Setup ──────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))
from ml.config import (
    IMPORT_RESELLERS, EXCLUDED_SERIES, MIN_OBSERVATIONS,
    DEFAULT_CHANGEPOINT_PRIOR_SCALE, CHANGEPOINT_OVERRIDES,
    PROPHET_SETTINGS, EXTRA_REGRESSORS,
    MODELS_DIR, MART_ML_SCHEMA, MART_ML_TABLE,
    S3_BUCKET, S3_MODEL_PREFIX,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)
logging.getLogger('prophet').setLevel(logging.WARNING)
logging.getLogger('cmdstanpy').setLevel(logging.WARNING)


# ── S3 ─────────────────────────────────────────────────────────────────────
def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name=os.environ.get('AWS_REGION', 'ap-southeast-2'),
    )


def upload_model_to_s3(s3, model: Prophet, model_key: str) -> str:
    """Serialize model to bytes and upload to S3."""
    buffer = BytesIO()
    pickle.dump(model, buffer)
    buffer.seek(0)

    s3_key = f"{S3_MODEL_PREFIX}{model_key}.pkl"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=buffer.getvalue(),
        ContentType='application/octet-stream',
    )
    return s3_key


def cache_model_locally(model: Prophet, model_key: str) -> Path:
    """Also save model to local cache for faster subsequent local runs."""
    path = MODELS_DIR / f"{model_key}.pkl"
    with open(path, 'wb') as f:
        pickle.dump(model, f)
    return path


# ── Database ───────────────────────────────────────────────────────────────
def get_engine():
    host     = os.environ['POSTGRES_HOST']
    port     = os.environ['POSTGRES_PORT']
    user     = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    dbname   = os.environ['POSTGRES_DB']
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"
    return create_engine(url)


def load_mart_ml(engine) -> pd.DataFrame:
    query = text(f"SELECT * FROM {MART_ML_SCHEMA}.{MART_ML_TABLE} ORDER BY product_name, seller, ds")
    df = pd.read_sql(query, engine)
    df['ds'] = pd.to_datetime(df['ds'])
    return df


# ── Filtering ──────────────────────────────────────────────────────────────
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    df = df[~df['seller'].isin(IMPORT_RESELLERS)].copy()
    series_counts = df.groupby(['product_name', 'seller']).size()
    tier1_keys = series_counts[series_counts >= MIN_OBSERVATIONS].index
    df = df.set_index(['product_name', 'seller']).loc[tier1_keys].reset_index()
    exclude_mask = df.apply(
        lambda r: (r['product_name'], r['seller']) in EXCLUDED_SERIES, axis=1
    )
    df = df[~exclude_mask].copy()
    log.info(f"Filtered dataset: {len(df)} rows, "
             f"{df.groupby(['product_name','seller']).ngroups} series")
    return df


# ── Series helpers ─────────────────────────────────────────────────────────
def get_series(df: pd.DataFrame, product_name: str, seller: str) -> pd.DataFrame:
    cols = ['ds', 'y'] + EXTRA_REGRESSORS
    return (
        df[(df['product_name'] == product_name) & (df['seller'] == seller)][cols]
        .sort_values('ds')
        .drop_duplicates(subset='ds')
        .reset_index(drop=True)
    )


def make_model_key(product_name: str, seller: str) -> str:
    safe = lambda s: s.replace(' ', '_').replace('/', '-').replace('.', '')
    return f"{safe(product_name)}__{safe(seller)}"


# ── Training ───────────────────────────────────────────────────────────────
def train_series(series: pd.DataFrame, product_name: str, seller: str) -> Prophet:
    cps = CHANGEPOINT_OVERRIDES.get(
        (product_name, seller),
        DEFAULT_CHANGEPOINT_PRIOR_SCALE
    )
    m = Prophet(changepoint_prior_scale=cps, **PROPHET_SETTINGS)
    for regressor in EXTRA_REGRESSORS:
        m.add_regressor(regressor)
    m.fit(series[['ds', 'y'] + EXTRA_REGRESSORS])
    return m


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    start = datetime.now()
    log.info("=== Prophet Training Script ===")
    log.info(f"S3 bucket: s3://{S3_BUCKET}/{S3_MODEL_PREFIX}")

    engine = get_engine()
    s3     = get_s3_client()

    log.info("Connecting to Neon...")
    df_raw = load_mart_ml(engine)
    log.info(f"Loaded mart_ml: {df_raw.shape[0]} rows")

    df = apply_filters(df_raw)

    series_list = (
        df.groupby(['product_name', 'seller'])
        .size()
        .reset_index(name='n_rows')
        .sort_values('product_name')
    )

    log.info(f"Training {len(series_list)} series...")

    succeeded = []
    failed    = []

    for _, row in series_list.iterrows():
        product = row['product_name']
        seller  = row['seller']
        n_rows  = row['n_rows']

        try:
            series    = get_series(df, product, seller)

            if len(series) < 20:
                raise ValueError(f"Too few rows: {len(series)}")

            model     = train_series(series, product, seller)
            key       = make_model_key(product, seller)

            # Upload to S3 (production storage)
            s3_key    = upload_model_to_s3(s3, model, key)

            # Cache locally (speeds up local predict.py runs)
            cache_model_locally(model, key)

            cps_used  = CHANGEPOINT_OVERRIDES.get(
                (product, seller), DEFAULT_CHANGEPOINT_PRIOR_SCALE
            )
            log.info(f"  ✅ {product[:22]:<22} | {seller[:28]:<28} | "
                     f"n={n_rows:<3} cps={cps_used} → s3://{S3_BUCKET}/{s3_key}")
            succeeded.append(product)

        except Exception as e:
            log.error(f"  ❌ {product[:22]:<22} | {seller[:28]:<28} | ERROR: {e}")
            failed.append({'product': product, 'seller': seller, 'error': str(e)})

    elapsed = (datetime.now() - start).seconds
    log.info(f"\n=== Training Complete ===")
    log.info(f"Succeeded: {len(succeeded)} series")
    log.info(f"Failed:    {len(failed)} series")
    log.info(f"Time:      {elapsed}s")

    if failed:
        log.warning("Failed series:")
        for f in failed:
            log.warning(f"  {f['product']} / {f['seller']}: {f['error']}")

    return len(failed) == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)