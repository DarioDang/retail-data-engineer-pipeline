# Overview Queries 

# These are identical to streamlit 
# No SQL changes needed - FastAPI runs the exact same queries against

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
 
# ── Time-aware insight queries ─────────────────────────────────────────────────
 
PRICE_CHANGE_VS_YESTERDAY = """
    WITH latest AS (
        SELECT
            product_name,
            category,
            avg_price,
            snapshot_date,
            LAG(avg_price) OVER (
                PARTITION BY product_name ORDER BY snapshot_date
            ) AS prev_price
        FROM dev_marts.fact_price_changes
    ),
    ranked AS (
        SELECT *,
            ROUND(((avg_price - prev_price) / prev_price * 100)::numeric, 2) AS pct_change,
            ROW_NUMBER() OVER (PARTITION BY product_name ORDER BY snapshot_date DESC) AS rn
        FROM latest
        WHERE prev_price IS NOT NULL
    )
    SELECT
        product_name,
        category,
        avg_price,
        prev_price,
        pct_change,
        snapshot_date
    FROM ranked
    WHERE rn = 1
    ORDER BY ABS(pct_change) DESC
"""
 
PRICE_CHANGE_VS_LAST_WEEK = """
    WITH all_dates AS (
        SELECT DISTINCT snapshot_date
        FROM dev_marts.fact_price_changes
        ORDER BY snapshot_date DESC
    ),
    latest AS (
        SELECT snapshot_date AS today_date
        FROM all_dates
        LIMIT 1
    ),
    oldest AS (
        SELECT snapshot_date AS old_date
        FROM all_dates
        ORDER BY snapshot_date ASC
        LIMIT 1
    ),
    today_prices AS (
        SELECT product_name, category, avg_price AS today_price
        FROM dev_marts.fact_price_changes
        WHERE snapshot_date = (SELECT today_date FROM latest)
    ),
    old_prices AS (
        SELECT product_name, avg_price AS week_price
        FROM dev_marts.fact_price_changes
        WHERE snapshot_date = (SELECT old_date FROM oldest)
    ),
    joined AS (
        SELECT
            t.product_name,
            t.category,
            t.today_price,
            w.week_price,
            ROUND(
                ((t.today_price - w.week_price) / NULLIF(w.week_price, 0) * 100)::numeric, 2
            ) AS pct_change_week
        FROM today_prices t
        JOIN old_prices w ON t.product_name = w.product_name
    )
    SELECT * FROM joined
    ORDER BY ABS(pct_change_week) DESC
"""
 
PRICE_STATS_LAST_7_DAYS = """
    WITH last_7 AS (
        SELECT
            product_name,
            category,
            avg_price,
            snapshot_date
        FROM dev_marts.fact_price_changes
        WHERE snapshot_date >= (
            SELECT MAX(snapshot_date) - 6
            FROM dev_marts.fact_price_changes
        )
    )
    SELECT
        product_name,
        category,
        MAX(avg_price)  AS max_price_7d,
        MIN(avg_price)  AS min_price_7d,
        AVG(avg_price)  AS avg_price_7d,
        MAX(snapshot_date) AS latest_date
    FROM last_7
    GROUP BY product_name, category
    ORDER BY max_price_7d DESC
"""

CHEAPEST_SELLER_PER_CATEGORY = """
    WITH ranked AS (
        SELECT product_name, category, seller, price,
            AVG(price) OVER (PARTITION BY category) AS avg_price,
            ROW_NUMBER() OVER (PARTITION BY category ORDER BY price ASC) AS rn
        FROM dev_staging.stg_electronic_products
        WHERE snapshot_date = (
            SELECT MAX(snapshot_date) FROM dev_staging.stg_electronic_products
        )
    )
    SELECT category, product_name, seller,
        ROUND(price::numeric, 2) AS min_price,
        ROUND(avg_price::numeric, 2) AS avg_price,
        ROUND(((avg_price - price) / avg_price * 100)::numeric, 1) AS savings_pct
    FROM ranked WHERE rn = 1 ORDER BY category
"""