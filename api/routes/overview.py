from fastapi import APIRouter, HTTPException
from api.db import run_query 
from api.cache import cache
from api import queries

router = APIRouter()

def _safe_query(cache_key: str, sql:str) -> list[dict]:
    """
    Helper that runs a cached query and converts the DataFrame to a list of dicts - the format JSON response expect.

    If the database is unreachable or the query fails, FastAPI returns a clean 500 error instead of crashing with an
    unhandled exception.
    """

    try:
        df = cache.cached_query(cache_key, lambda: run_query(sql))

        # convert NaN to None so JSON serialisation does not break
        return df.where(df.notna(), other = None).to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
    
# KPI Cards 
@router.get("/total-listings")
def total_listings():
    """
    Return the total number of price snapshot rows.
    Used by the "Total Listings" KPI card on the Overview page.
    Response: {"total": 1234}
    """

    rows = _safe_query("overview_total_listings", queries.TOTAL_LISTINGS)
    return rows[0] if rows else {"total": 0}

@router.get("/total-products")
def total_products():
    """
    Return count of distinct products in dim_product.
    Used by the "Total Products" KPI card.
    Response: {"total": 8}
    """

    rows = _safe_query("overview_total_products", queries.TOTAL_PRODUCTS)
    return rows[0] if rows else {"total": 0}

@router.get("/total-sellers")
def total_sellers():
    """
    Returns count of distinct sellers in dim_store.
    Used by the 'Total Sellers' KPI card.
    Response: { "total": 42 }
    """

    rows = _safe_query("overview_total_sellers", queries.TOTAL_SELLERS)
    return rows[0] if rows else {"total": 0}

# Charts 
@router.get("/listings-by-seller")
def listings_by_seller():
    """
    Top 15 sellers by listing count.
    Used by the seller distribution bar chart.
    Response: [{ "seller": "PB Tech", "listings": 24 }, ...] 
    """
    return _safe_query("overview_listings_by_seller", queries.LISTING_BY_SELLER)

@router.get("/listings-by-category")
def listings_by_category():
    """
    Listing count grouped by category.
    Used by the category distribution chart.
    Response: [{ "category": "Laptop", "listings": 120 }, ...]
    """
    return _safe_query("overview_listings_by_category", queries.LISTINGS_BY_CATEGORY)