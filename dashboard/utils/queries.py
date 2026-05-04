# Overview Queries
TOTAL_LISTINGS = """
    SELECT COUNT(*) as total
    FROM dev_marts.fact_price_snapshot
"""

TOTAL_PRODUCTS = """
    SELECT COUNT(DISTINCT product_name) as total
    FROM dev_marts.dim_product
"""

TOTAL_SELLERS = """
    SELECT COUNT(DISTINCT store_name) as total
    FROM dev_marts.dim_store
"""

LISTING_BY_SELLER = """
    SELECT 
        seller,
        COUNT(*) as listings
    FROM dev_marts.fact_price_snapshot
    GROUP BY seller
    ORDER BY listings DESC
    LIMIT 15
"""

LISTINGS_BY_CATEGORY = """
    SELECT 
        category,
        COUNT(*) as listings
    FROM dev_marts.fact_price_snapshot
    GROUP BY category
    ORDER BY listings DESC
"""

# ── Price Analysis Queries ─────────────────────────────────────────────────────

AVG_PRICE_OVER_TIME = """
    SELECT 
        snapshot_date,
        product_name,
        category,
        avg_price
    FROM dev_marts.fact_price_changes
    ORDER BY snapshot_date, product_name
"""

PRICE_STATS_PER_PRODUCT = """
    SELECT
        p.product_name,
        p.category,
        p.seller_count,
        p.min_price,
        p.max_price,
        p.avg_price,
        p.cheapest_seller,
        p.cheapest_price,
        ROUND(((p.avg_price - p.cheapest_price) / p.avg_price * 100)::numeric, 2) AS savings_pct,
        ROUND(AVG(f.rating)::numeric, 2)  AS avg_rating,
        SUM(f.reviews)                    AS avg_reviews
    FROM dev_marts.agg_seller_per_product p
    LEFT JOIN dev_marts.fact_price_snapshot f
           ON f.product_name = p.product_name
    GROUP BY
        p.product_name, p.category, p.seller_count,
        p.min_price, p.max_price, p.avg_price,
        p.cheapest_seller, p.cheapest_price
    ORDER BY p.category, p.product_name
"""

PRICE_RANGE_BY_PRODUCT = """
    SELECT
        product_name,
        category,
        price
    FROM dev_marts.fact_price_snapshot
    ORDER BY category, product_name
"""

DISCOUNT_PRODUCTS = """
    SELECT
        product_name,
        seller,
        price,
        old_price,
        discount_pct
    FROM dev_marts.fact_price_snapshot
    WHERE discount_pct IS NOT NULL
    ORDER BY discount_pct DESC
"""

# ── Seller Intelligence Queries ────────────────────────────────────────────────

SELLER_COUNT_PER_PRODUCT = """
    SELECT
        product_name,
        category,
        seller_count
    FROM dev_marts.agg_seller_per_product
    ORDER BY seller_count DESC
"""

CHEAPEST_SELLER_PER_PRODUCT = """
    SELECT
        product_name,
        category,
        cheapest_seller,
        cheapest_price,
        avg_price,
        ROUND(((avg_price - cheapest_price) / avg_price * 100)::numeric, 2) as savings_pct
    FROM dev_marts.agg_seller_per_product
    ORDER BY category, product_name
"""

RATING_BY_SELLER = """
    SELECT
        seller,
        ROUND(AVG(rating)::numeric, 2) as avg_rating,
        SUM(reviews) as total_reviews,
        COUNT(*) as total_listings
    FROM dev_marts.fact_price_snapshot
    WHERE has_rating = true
    GROUP BY seller
    HAVING COUNT(*) >= 2
    ORDER BY avg_rating DESC
    LIMIT 15
"""

RATING_STATUS_DISTRIBUTION = """
    SELECT
        rating_status,
        COUNT(*) as count
    FROM dev_marts.fact_price_snapshot
    GROUP BY rating_status
    ORDER BY count DESC
"""

CATEGORY_SUMMARY = """
    SELECT
        category,
        product_count,
        seller_count,
        total_listings,
        min_price,
        max_price,
        avg_price
    FROM dev_marts.agg_category_summary
    ORDER BY category
"""