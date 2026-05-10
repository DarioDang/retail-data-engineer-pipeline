import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd

# Load .env from project root (two levels up from api/)
load_dotenv(Path(__file__).parent.parent / ".env")

def get_db_config() -> dict:
    """
        Read RDS credentials from environment variables.
        These come from the .env file locally or from the environment
        variables injected by Render / Railway when deployed to cloud.    
    """

    return {
        "user":     os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host":     os.getenv("POSTGRES_HOST"),
        "port":     os.getenv("POSTGRES_PORT", "5432"),
        "db":       os.getenv("POSTGRES_DB"),
    }

def get_engine():
    """
       Create a SQLAlchemy engine with a connection pool.
 
        QueuePool keeps a small number of connections open and reuses them,
        so FastAPI does not open a new connection to RDS on every request.
        This is important for AWS RDS which has a max-connections limit.
    
        pool_size=5   → keep 5 connections open at all times
        max_overflow=5 → allow up to 5 extra connections under heavy load
        pool_recycle=1800 → close and reopen connections every 30 min
                            (prevents "connection gone away" errors on RDS)
    """

    cfg = get_db_config()
    url = (
        f"postgresql://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['db']}"
    )

    return create_engine(
        url,
        poolclass = QueuePool,
        pool_size = 5,
        max_overflow = 5,
        pool_recycle = 1800,
        pool_pre_ping=True
    )

# Single engine instance shared across the whole app
# Fast API starts once and this runs once at startup.
engine = get_engine()


def run_query(sql: str) -> pd.DataFrame:
    """
    Execute a SQL string and return a pandas DataFrame.
 
    Unlike the Streamlit version, there is no @st.cache_data here.
    Caching in FastAPI is handled at the route level using
    a simple in-memory TTL cache (see cache.py).
    """

    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)