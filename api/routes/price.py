from fastapi import APIRouter, HTTPException 
from api.db import run_query
from api.cache import cache
from api import queries

router = APIRouter()

def _safe_query(cache_key: str, sql: str) -> list[dict]:
    try:
        df = cache.cached_query(cache_key, lambda: run_query(sql))
        return df.where(df.notna(), other=None).to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ── Charts ─────────────────────────────────────────────────────────────────────
 
@router.get("/avg-price-over-time")
def avg_price_over_time():
    """
    Average price per product per day across all snapshot dates.
    Used by the main price trend line chart.
    Response: [{ "snapshot_date": "2026-05-01", "product_name": "...",
                 "category": "Laptop", "avg_price": 1299.99 }, ...]
    
    Note: snapshot_date comes back as a Python date object.
    FastAPI serialises it as an ISO string ("2026-05-01") automatically.
    Plotly.js on the frontend reads it directly as a date axis.
    """
    return _safe_query("price_avg_over_time", queries.AVG_PRICE_OVER_TIME)
 
 
@router.get("/stats-per-product")
def stats_per_product():
    """
    Full price stats per product: min, max, avg, cheapest seller, savings %.
    Also includes avg rating and total reviews joined from fact_price_snapshot.
    Used by the product stats table and the KPI carousel.
    Response: [{ "product_name": "...", "category": "...", "seller_count": 5,
                 "min_price": 999, "max_price": 1499, "avg_price": 1199,
                 "cheapest_seller": "...", "cheapest_price": 999,
                 "savings_pct": 16.68, "avg_rating": 4.5,
                 "avg_reviews": 2300 }, ...]
    """
    return _safe_query("price_stats_per_product", queries.PRICE_STATS_PER_PRODUCT)
 
 
@router.get("/price-range-by-product")
def price_range_by_product():
    """
    Every individual price listing per product.
    Used by the box plot / price range chart showing spread across sellers.
    Response: [{ "product_name": "...", "category": "...", "price": 1199.0 }, ...]
    """
    return _safe_query("price_range_by_product", queries.PRICE_RANGE_BY_PRODUCT)
 
 
@router.get("/discounts")
def discounts():
    """
    All listings that have a discount_pct, ordered highest discount first.
    Used by the discount leaderboard table.
    Response: [{ "product_name": "...", "seller": "...", "price": 799,
                 "old_price": 999, "discount_pct": 20.0 }, ...]
    """
    return _safe_query("price_discounts", queries.DISCOUNT_PRODUCTS)
 
 
# ── Time-aware insights ────────────────────────────────────────────────────────
 
@router.get("/change-vs-yesterday")
def change_vs_yesterday():
    """
    Latest price vs the previous day's price per product.
    Uses a window function (LAG) so no date parameter needed.
    Used by the 'Price Change vs Yesterday' chart/table.
    Response: [{ "product_name": "...", "category": "...",
                 "avg_price": 1250, "prev_price": 1299,
                 "pct_change": -3.77, "snapshot_date": "2026-05-09" }, ...]
    """
    return _safe_query("price_change_yesterday", queries.PRICE_CHANGE_VS_YESTERDAY)
 
 
@router.get("/change-vs-last-week")
def change_vs_last_week():
    """
    Today's price vs the oldest available date in the dataset.
    Used by the 'Price Change vs Last Week' chart.
    Response: [{ "product_name": "...", "category": "...",
                 "today_price": 1250, "week_price": 1299,
                 "pct_change_week": -3.77 }, ...]
    """
    return _safe_query("price_change_week", queries.PRICE_CHANGE_VS_LAST_WEEK)
 
 
@router.get("/stats-last-7-days")
def stats_last_7_days():
    """
    Max, min, avg price per product over the last 7 snapshot days.
    Used by the rolling 7-day KPI cards (most expensive, lowest avg, etc.).
    Response: [{ "product_name": "...", "category": "...",
                 "max_price_7d": 1499, "min_price_7d": 999,
                 "avg_price_7d": 1199.5, "latest_date": "2026-05-09" }, ...]
    """
    return _safe_query("price_stats_7d", queries.PRICE_STATS_LAST_7_DAYS)