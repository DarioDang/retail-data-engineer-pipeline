"""
Shared Neon PostgreSQL connection helper fir Jupyter Notebooks

Usage in a notebook:
    import sys
    sys.path.append("..") #if notebook is inside notebooks/
    from utils.db import get_engine, load mart_ml

    engine = get_engine()
    df = load_mart_ml(engine)
"""

import os 
from pathlib import Path 
from sqlalchemy import create_engine, text
import pandas as pd 
from dotenv import load_dotenv

# Load .env from project root, regardless of where the notebook is run from 
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

def get_engine():
    """
    Build a SQLAlchemy engine connected to Neon using credentials from .env.
    Requires sslmode= require, which Neon enfroces.
    """

    host = os.environ["POSTGRES_HOST"]
    port = os.environ["POSTGRES_PORT"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    dbname = os.environ["POSTGRES_DB"]

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"
    engine = create_engine(url)
    return engine

def load_mart_ml(engine, schema: str = "dev_marts") -> pd.DataFrame:
    """
    Load the full mart_ml table into a pandas DataFrame.
    """

    query = text(f"SELECT * FROM {schema}.mart_ml ORDER BY product_name, seller, ds")
    df = pd.read_sql(query, engine)
    return df

def test_connection(engine):
    """
    Quick sanity check - confirms connection works and prints row count + date range.
    """ 

    with engine.connect() as conn:
        result = conn.execute(text("SELECT MIN(ds), MAX(ds), COUNT(*) FROM dev_marts.mart_ml"))
        row = result.fetchone()
        print(f"Connected. Date range: {row[0]} to {row[1]} | Total rows: {row[2]}")