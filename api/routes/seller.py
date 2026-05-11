from fastapi import APIRouter, HTTPException 
from api.db import run_query
from api.cache import cache
from api import queries

router = APIRouter()

def _safe_query(cache_key: str, sql:str) -> list[dict]:
    try:
        df = cache.cached_query(cache_key, lambda: run_query(sql))
        return df.where(df.notna(), other = None).to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/seller-count-per-product")
def seller_count_per_product():
    """
    How many sellers list each product
    """
    return _safe_query("seller_count_per_product", queries.SELLER_COUNT_PER_PRODUCT)

@router.get("/cheapest-seller-per-product")
def cheapest_seller_per_product():
    """
    The cheapest seller and their price vs the average, per product.
    Used by the 'Best Deal' table.
    """
    return _safe_query("seller_cheapest_per_product", queries.CHEAPEST_SELLER_PER_PRODUCT)
 
@router.get("/rating-by-seller")
def rating_by_seller():
    """
    Top 15 sellers by average rating (minimum 2 listings to qualify).
    Used by the seller rating bar chart."""
    return _safe_query("seller_rating_by_seller", queries.RATING_BY_SELLER)

@router.get("/rating-status-distribution")
def rating_status_distribution():
    """
    Distribution of rating statuses across all listings.
    Used by the rating status pie chart.
    """
    return _safe_query("seller_rating_status_distribution", queries.RATING_STATUS_DISTRIBUTION)

@router.get("/category-summary")
def category_summary():
    """
    Aggregated stats per category: product count, seller count,
    total listings, price range.
    """
    return _safe_query("seller_category_summary", queries.CATEGORY_SUMMARY)

@router.get("/cheapest-seller-per-category")
def cheapest_seller_per_category():
    """
    The single cheapest seller per category on the latest snapshot date.
    """
    return _safe_query("seller_cheapest_per_category", queries.CHEAPEST_SELLER_PER_CATEGORY)