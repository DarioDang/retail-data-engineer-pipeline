import os 
import pandas as pd
from sqlalchemy import create_engine, text 
from dotenv import load_dotenv
from pathlib import Path

# Load dashboard specific .env
load_dotenv(Path(__file__).parent.parent / ".env")

def get_engine():
    """Create a SQLAlchemy engine using environment variables."""
    return create_engine(
        f"postgresql://"
        f"{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )

def run_query(sql: str):
    """ Execute SQL and return DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


