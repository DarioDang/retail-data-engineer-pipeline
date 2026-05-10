import time
import pandas as pd
from typing import Callable
from datetime import datetime
import pytz


def get_cache_ttl() -> int:
    nz_tz = pytz.timezone("Pacific/Auckland")
    now = datetime.now(nz_tz)
    next_pipeline = now.replace(hour=20, minute=0, second=0, microsecond=0)
    if now >= next_pipeline:
        from datetime import timedelta
        next_pipeline += timedelta(days=1)
    return int((next_pipeline - now).total_seconds())


class QueryCache:
    def __init__(self):
        self.store = {}

    def get(self, key: str):
        if key in self.store:
            df, expiry = self.store[key]
            if time.time() < expiry:
                return df
            del self.store[key]
        return None

    def set(self, key: str, df: pd.DataFrame, ttl: int) -> None:
        self.store[key] = (df, time.time() + ttl)

    def cached_query(self, key: str, query_fn: Callable[[], pd.DataFrame]) -> pd.DataFrame:
        cached = self.get(key)
        if cached is not None:
            return cached
        df = query_fn()
        self.set(key, df, ttl=get_cache_ttl())
        return df


cache = QueryCache()