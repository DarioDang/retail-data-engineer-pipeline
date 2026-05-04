import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import pytz

# Load local .env (only works locally, ignored on Streamlit Cloud)
load_dotenv(Path(__file__).parent.parent / ".env")

def get_db_config():
    """Get DB config from Streamlit secrets (cloud) or .env (local)."""
    try:
        return {
            "user": st.secrets["database"]["username"],
            "password": st.secrets["database"]["password"],
            "host": st.secrets["database"]["host"],
            "port": st.secrets["database"]["port"],
            "db": st.secrets["database"]["database"],
        }
    except Exception:
        return {
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "host": os.getenv("POSTGRES_HOST"),
            "port": os.getenv("POSTGRES_PORT"),
            "db": os.getenv("POSTGRES_DB"),
        }

def get_engine():
    """Create a SQLAlchemy engine."""
    cfg = get_db_config()
    return create_engine(
        f"postgresql://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['db']}"
    )

def get_cache_ttl() -> int:
    """
    Return cache TTL in seconds.
    - Between 8:00pm - 8:30pm NZT → no cache (0 seconds)
      so users see fresh data right after pipeline runs
    - All other times → 55 minute cache
    """
    nz_tz = pytz.timezone("Pacific/Auckland")
    now = datetime.now(nz_tz)
    hour = now.hour
    minute = now.minute

    # Pipeline runs at 8pm NZT — disable cache 8:00-8:30pm
    if hour == 20 and minute <= 30:
        return 0  # no cache during pipeline window

    return 55 * 60  # 55 minutes in seconds

@st.cache_data(ttl=get_cache_ttl())
def run_query(sql: str) -> pd.DataFrame:
    """Execute SQL and return DataFrame with smart caching."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)