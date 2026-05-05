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
    WITH daily AS (
        SELECT
            product_name,
            category,
            avg_price,
            snapshot_date
        FROM dev_marts.fact_price_changes
    ),
    latest_date AS (
        SELECT MAX(snapshot_date) AS max_date FROM daily
    ),
    week_ago_date AS (
        SELECT MAX(snapshot_date) AS week_ago
        FROM daily
        WHERE snapshot_date <= (
            SELECT max_date::date - 6 FROM latest_date
        )
    ),
    today AS (
        SELECT product_name, category, avg_price AS today_price, snapshot_date
        FROM daily
        WHERE snapshot_date = (SELECT max_date FROM latest_date)
    ),
    week_ago AS (
        SELECT product_name, avg_price AS week_price
        FROM daily
        WHERE snapshot_date = (SELECT week_ago FROM week_ago_date)
    )
    SELECT
        t.product_name,
        t.category,
        t.today_price,
        w.week_price,
        t.snapshot_date,
        ROUND(((t.today_price - w.week_price) / NULLIF(w.week_price, 0) * 100)::numeric, 2) AS pct_change_week
    FROM today t
    JOIN week_ago w ON t.product_name = w.product_name
    ORDER BY ABS(pct_change_week) DESC
"""