# ml/predict.py
# Production forecast script — downloads trained Prophet models from S3
# (with local cache fallback), generates 14-day forward forecasts,
# writes results to Neon mart_forecasts table.
#
# Usage:
#   cd ~/Desktop/Project/retail-data-engineer-pipeline
#   loadenv
#   pipenv run python ml/predict.py
#
# On Prefect managed workers: always downloads fresh models from S3.
# Locally: uses cached .pkl files if present, downloads from S3 if not.
# Safe to re-run — truncates and rewrites mart_forecasts each run.

import os
import sys
import pickle 
import logging 
import boto3 
import pandas as pd 
from io import BytesIO
from pathlib import Path
from datetime import datetime, date 
from prophet import Prophet
from sqlalchemy import create_engine, text
from botocore.exceptions import ClientError

# Setup logging
sys.path.insert(0, str(Path(__file__).parent.parent))
from ml.config import (
    IMPORT_RESELLERS, EXCLUDED_SERIES, MIN_OBSERVATIONS,
    EXTRA_REGRESSORS, MODELS_DIR,
    MART_ML_SCHEMA, MART_ML_TABLE,
    FORECASTS_SCHEMA, FORECASTS_TABLE,
    FORECAST_HORIZON_DAYS,
    TIER_A_MAPE_THRESHOLD, TIER_B_MAPE_THRESHOLD,
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

# S3 client
def get_s3_client():
    """
    Create and return an S3 client using boto3 with credentials from environment variables.
    """

    return boto3.client(
        's3',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name=os.environ.get('AWS_REGION', 'ap-southeast-2'),
    )

def load_model(s3, product_name: str, seller: str) -> Prophet:
    """
    Load a Prophet model — checks local cache first, downloads from S3 if missing.
    On Prefect workers (ephemeral filesystem) this always downloads from S3.
    Locally this uses the cache after the first download.
    """
    safe  = lambda s: s.replace(' ', '_').replace('/', '-').replace('.', '')
    key   = f"{safe(product_name)}__{safe(seller)}"
    local = MODELS_DIR / f"{key}.pkl"
    s3_key = f"{S3_MODEL_PREFIX}{key}.pkl"

    # Try local cache first
    if local.exists():
        with open(local, 'rb') as f:
            return pickle.load(f)

    # Download from S3
    try:
        log.info(f"    Downloading from S3: {s3_key}")
        response = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
        model_bytes = response['Body'].read()

        # Cache locally for future runs
        local.parent.mkdir(exist_ok=True)
        with open(local, 'wb') as f:
            f.write(model_bytes)

        return pickle.loads(model_bytes)

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            log.warning(f"Model not found in S3: {s3_key}")
        else:
            log.error(f"S3 error loading {s3_key}: {e}")
        return None
    
# Database connection
def get_engine():
    """
    Create and return a SQLAlchemy engine for the PostgreSQL database using environment variables.
    """
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


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    df = df[~df['seller'].isin(IMPORT_RESELLERS)].copy()
    series_counts = df.groupby(['product_name', 'seller']).size()
    tier1_keys = series_counts[series_counts >= MIN_OBSERVATIONS].index
    df = df.set_index(['product_name', 'seller']).loc[tier1_keys].reset_index()
    exclude_mask = df.apply(
        lambda r: (r['product_name'], r['seller']) in EXCLUDED_SERIES, axis=1
    )
    return df[~exclude_mask].copy()


def get_series(df: pd.DataFrame, product_name: str, seller: str) -> pd.DataFrame:
    cols = ['ds', 'y'] + EXTRA_REGRESSORS
    return (
        df[(df['product_name'] == product_name) & (df['seller'] == seller)][cols]
        .sort_values('ds')
        .drop_duplicates(subset='ds')
        .reset_index(drop=True)
    )

# Forecasting
def generate_forecast(model: Prophet, series: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a forward-looking forecast from today, regardless of when the
    last observation was. Series with data gaps (seller disappeared from
    search results) still get a forecast — Prophet extrapolates the trend.
    """
    today      = pd.Timestamp(date.today())
    last_known = series['ds'].max()

    # Calculate how many periods needed to reach today + horizon
    # If last_known is recent, this is just FORECAST_HORIZON_DAYS
    # If there's a gap, we extend periods to cover the gap + horizon
    days_since_last = max(0, (today - last_known).days)
    periods_needed  = days_since_last + FORECAST_HORIZON_DAYS

    future = model.make_future_dataframe(periods=periods_needed)

    for regressor in EXTRA_REGRESSORS:
        future = future.merge(series[['ds', regressor]], on='ds', how='left')
        future[regressor] = future[regressor].fillna(0).astype(int)

    forecast = model.predict(future)

    # Only return rows from today forward
    result = forecast[
        forecast['ds'] >= today
    ][['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()

    # Trim to exactly FORECAST_HORIZON_DAYS rows
    result = result.head(FORECAST_HORIZON_DAYS).copy()

    for col in ['yhat', 'yhat_lower', 'yhat_upper']:
        result[col] = result[col].round(2)

    return result

# ── MAPE lookup ────────────────────────────────────────────────────────────
SERIES_MAPE = {
    ('Dell XPS 13', 'eBay - grassroots-computers'):          1.40,
    ('Dell XPS 13', 'eBay - new.techies'):                   3.60,
    ('Dell XPS 13', 'eBay - r3newtech'):                     1.66,
    ('Dell XPS 13', 'eBay - toptechgears'):                  2.20,
    ('GoPro Hero 13', 'JB Hi-Fi'):                          11.98,
    ('GoPro Hero 13', 'UwCameraStore.com'):                   7.60,
    ('GoPro Hero 13', 'eBay'):                                0.99,
    ('GoPro Hero 13', 'eBay - thepixelhub'):                  3.40,
    ('HP Spectre x360', 'eBay - zmh688'):                     1.30,
    ('HP Spectre x360', 'eBay - surpluserecycle'):            0.97,
    ('HP Spectre x360', 'eBay - oz.gadgets'):                 1.22,
    ('HP Spectre x360', 'PB Tech'):                           4.38,
    ('HP Spectre x360', 'eBay - bestcomputerdeal'):           1.82,
    ('HP Spectre x360', 'TieDex'):                            0.50,
    ('HP Spectre x360', 'eBay - entique_australia'):          6.60,
    ('MacBook Air M3', 'eBay'):                               1.67,
    ('MacBook Air M3', 'eBay - bq_shop01'):                   4.81,
    ('MacBook Air M3', 'PB Tech'):                            4.70,
    ('MacBook Air M3', 'Microless.com'):                      4.72,
    ('MacBook Air M3', 'Dick Smith NZ'):                      8.38,
    ('MacBook Air M3', 'AliExpress'):                         4.11,
    ('MacBook Air M3', 'MightyApe.co.nz'):                   12.94,
    ('Samsung Galaxy A54', 'AliExpress'):                     7.95,
    ('Samsung Galaxy A54', 'eBay - kickmobiles-ltd'):         1.23,
    ('Samsung Galaxy A54', 'eBay - panda_electronic_au'):     0.66,
    ('Samsung Galaxy A54', 'eBay - soundsolutions_worldwide'): 1.48,
    ('Samsung Galaxy A54', 'eBay - xwcellphone'):             6.64,
    ('Samsung Galaxy S24', 'BecexTech New Zealand'):          3.28,
    ('Samsung Galaxy S24', 'Reebelo NZ'):                     4.14,
    ('Samsung Galaxy S24', 'eBay - kickmobiles-ltd'):         7.51,
    ('Samsung Galaxy S24', 'eBay - soundsolutions_worldwide'): 4.18,
    ('Samsung Galaxy S24', 'eBay - yywirelesss'):            26.46,
    ('iPhone 15', 'Reebelo NZ'):                              6.88,
    ('iPhone 15', 'JB Hi-Fi'):                                0.11,
    ('iPhone 15', 'applefix.co.nz'):                          0.61,
}


def get_confidence_tier(mape: float) -> str:
    if mape < TIER_A_MAPE_THRESHOLD:
        return 'A'
    elif mape < TIER_B_MAPE_THRESHOLD:
        return 'B'
    return 'C'

# Database write
def create_forecasts_table(engine):
    """
    Create the mart_forecasts table if it does not exist. The table has the following columns:
    - id: SERIAL PRIMARY KEY
    - product_name: TEXT NOT NULL
    - seller: TEXT NOT NULL
    - forecast_date: DATE NOT NULL
    - forecast_run_date: DATE NOT NULL
    - yhat: NUMERIC(10,2) NOT NULL
    - yhat_lower: NUMERIC(10,2) NOT NULL
    - yhat_upper: NUMERIC(10,2) NOT NULL
    - mape: NUMERIC(6,2)
    - confidence_tier: TEXT
    - created_at: TIMESTAMPTZ DEFAULT NOW()  
    """
    with engine.connect() as conn:
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {FORECASTS_SCHEMA}.{FORECASTS_TABLE} (
                id                SERIAL PRIMARY KEY,
                product_name      TEXT          NOT NULL,
                seller            TEXT          NOT NULL,
                forecast_date     DATE          NOT NULL,
                forecast_run_date DATE          NOT NULL,
                yhat              NUMERIC(10,2) NOT NULL,
                yhat_lower        NUMERIC(10,2) NOT NULL,
                yhat_upper        NUMERIC(10,2) NOT NULL,
                mape              NUMERIC(6,2),
                confidence_tier   TEXT,
                created_at        TIMESTAMPTZ   DEFAULT NOW()
            )
        """))
        conn.commit()
    log.info(f"Table {FORECASTS_SCHEMA}.{FORECASTS_TABLE} ready")

def write_forecasts(engine, rows: list[dict]):
    """
    Write forecast rows to the mart_forecasts table. Each row should be a dictionary with keys:
    - product_name
    - seller
    - forecast_date
    - forecast_run_date
    - yhat
    - yhat_lower
    - yhat_upper
    - mape
    - confidence_tier   
    """
    if not rows:
        log.warning("No forecast rows to write")
        return

    df = pd.DataFrame(rows)

    with engine.connect() as conn:
        conn.execute(text(
            f"TRUNCATE TABLE {FORECASTS_SCHEMA}.{FORECASTS_TABLE}"
        ))
        df.to_sql(
            FORECASTS_TABLE,
            conn,
            schema=FORECASTS_SCHEMA,
            if_exists='append',
            index=False,
            method='multi'
        )
        conn.commit()

    log.info(f"Wrote {len(df)} forecast rows to "
             f"{FORECASTS_SCHEMA}.{FORECASTS_TABLE}")
    
# Main
def main():
    start    = datetime.now()
    run_date = date.today()
    log.info("=== Prophet Forecast Script ===")
    log.info(f"Run date: {run_date} | Horizon: {FORECAST_HORIZON_DAYS} days")
    log.info(f"S3 bucket: s3://{S3_BUCKET}/{S3_MODEL_PREFIX}")

    engine = get_engine()
    s3     = get_s3_client()

    log.info("Loading data from Neon...")
    df_raw = load_mart_ml(engine)
    df     = apply_filters(df_raw)

    series_list = (
        df.groupby(['product_name', 'seller'])
        .size()
        .reset_index(name='n_rows')
        .sort_values('product_name')
    )

    create_forecasts_table(engine)

    all_rows  = []
    succeeded = []
    failed    = []

    for _, row in series_list.iterrows():
        product = row['product_name']
        seller  = row['seller']

        try:
            model = load_model(s3, product, seller)
            if model is None:
                raise FileNotFoundError(f"No model in S3 or cache for {product} / {seller}")

            series      = get_series(df, product, seller)
            forecast_df = generate_forecast(model, series)

            if forecast_df.empty:
                raise ValueError("Forecast returned no future rows")

            mape = SERIES_MAPE.get((product, seller), None)
            tier = get_confidence_tier(mape) if mape is not None else 'C'

            for _, frow in forecast_df.iterrows():
                all_rows.append({
                    'product_name':      product,
                    'seller':            seller,
                    'forecast_date':     frow['ds'].date(),
                    'forecast_run_date': run_date,
                    'yhat':              frow['yhat'],
                    'yhat_lower':        frow['yhat_lower'],
                    'yhat_upper':        frow['yhat_upper'],
                    'mape':              mape,
                    'confidence_tier':   tier,
                })

            log.info(f"  ✅ {product[:22]:<22} | {seller[:28]:<28} | "
                     f"tier={tier} mape={mape}%")
            succeeded.append(product)

        except Exception as e:
            log.error(f"  ❌ {product[:22]:<22} | {seller[:28]:<28} | {e}")
            failed.append({'product': product, 'seller': seller, 'error': str(e)})

    if all_rows:
        write_forecasts(engine, all_rows)

    elapsed = (datetime.now() - start).seconds
    log.info(f"\n=== Forecast Complete ===")
    log.info(f"Succeeded: {len(succeeded)} | Failed: {len(failed)}")
    log.info(f"Rows written: {len(all_rows)} | Time: {elapsed}s")

    if failed:
        for f in failed:
            log.warning(f"  {f['product']} / {f['seller']}: {f['error']}")

    failure_rate = len(failed) / max(len(succeeded) + len(failed), 1)
    return failure_rate < 0.2  # fail only if >20% of series fail


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)