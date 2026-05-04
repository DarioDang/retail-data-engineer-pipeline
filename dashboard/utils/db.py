import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Load local .env (only works locally, ignored on Streamlit Cloud)
load_dotenv(Path(__file__).parent.parent / ".env")

def get_db_config():
    """Get DB config from Streamlit secrets (cloud) or .env (local)."""
    try:
        import streamlit as st
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

def run_query(sql: str):
    """Execute SQL and return DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)