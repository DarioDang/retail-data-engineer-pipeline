{{
    config(
        materialized='table',
    )
}}

-- ML training table: one row per product per seller per day
--
-- IMPORTANT: fact_price_snapshot has one row PER LISTING. Sellers commonly
-- list multiple variants of the same product on the same day. Tried two
-- earlier approaches that each broke down on different cases:
--   1. Averaging — broke when variant prices diverge sharply (e.g. GoPro
--      standard bundle ~$990 vs 2x-battery bundle ~$1977 averaged to a
--      meaningless ~$1480).
--   2. Cheapest, then cheapest-with-reviews — fixed most cases (a real
--      cheaper color variant correctly wins; a zero-review ghost listing
--      correctly loses), but failed when two listings share identical
--      rating/reviews metadata yet differ in price with no other
--      distinguishing field available in the scraped data (e.g. iPhone 15
--      "128GB" at $1150 vs $1649, same seller, same rating, same reviews,
--      on the same day — nothing in the data explains the difference).
--
-- Final approach: pick the listing closest to that seller's MOST FREQUENT
-- price for this product across the whole tracked period. A seller's
-- typical/persistent price (the one appearing on the most days) is the
-- best available proxy for "the standard price," regardless of why a
-- cheaper or pricier listing occasionally appears alongside it.

WITH base AS (
    SELECT 
        product_id,
        store_id,
        product_name,
        category,
        seller,
        snapshot_date,
        price,
        old_price,
        discount_pct,
        rating,
        reviews,
        rating_status
    FROM {{ ref('fact_price_snapshot') }}
    WHERE price IS NOT NULL
),

-- Round price to nearest $10 to group near-identical prices together
-- (e.g. $1650 and $1653 should count as "the same price" for frequency
-- purposes, not be split into two separate buckets).
price_buckets AS (
    SELECT
        *,
        ROUND(price / 10.0) * 10 AS price_bucket
    FROM base
),

-- Count how many days each price bucket appears for each product/seller
bucket_frequency AS (
    SELECT
        product_id,
        store_id,
        price_bucket,
        COUNT(*) AS bucket_days
    FROM price_buckets
    GROUP BY product_id, store_id, price_bucket
),

-- Identify each seller's single most frequent price bucket
most_frequent_bucket AS (
    SELECT DISTINCT ON (product_id, store_id)
        product_id,
        store_id,
        price_bucket AS typical_price_bucket
    FROM bucket_frequency
    ORDER BY product_id, store_id, bucket_days DESC, price_bucket ASC
),

-- Collapse same-day variants into one row per product/seller/day:
-- prefer the listing closest to the seller's typical price bucket.
daily_agg AS (
    SELECT DISTINCT ON (b.product_id, b.store_id, b.snapshot_date)
        b.product_id,
        b.store_id,
        b.product_name,
        b.category,
        b.seller,
        b.snapshot_date,
        b.price,
        b.old_price,
        b.discount_pct,
        b.rating,
        b.reviews,
        b.rating_status,
        COUNT(*) OVER (
            PARTITION BY b.product_id, b.store_id, b.snapshot_date
        ) AS variant_count

    FROM price_buckets b
    LEFT JOIN most_frequent_bucket m
        ON b.product_id = m.product_id
        AND b.store_id = m.store_id
    ORDER BY
        b.product_id, b.store_id, b.snapshot_date,
        ABS(b.price - m.typical_price_bucket) ASC,  -- closest to typical price wins
        b.price ASC                                   -- tie-break: cheapest
),

with_features AS (
    SELECT 
        -- keys --
        product_id,
        store_id,

        -- identifiers --
        product_name,
        category,
        seller,

        -- Prophet required columns --
        snapshot_date AS ds,
        price AS y,

        -- Lag features
        LAG(price, 1) OVER (PARTITION BY product_id, store_id ORDER BY snapshot_date) AS price_lag_1d,
        LAG(price, 7) OVER (PARTITION BY product_id, store_id ORDER BY snapshot_date) AS price_lag_7d,

        -- Rolling averages 
        AVG(price) OVER (
            PARTITION BY product_id, store_id
            ORDER BY snapshot_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW 
        ) AS price_ma_7d,

        AVG(price) OVER(
            PARTITION BY product_id, store_id
            ORDER BY snapshot_date
            ROWS BETWEEN 13 PRECEDING AND CURRENT ROW
        ) AS price_ma_14d,

        -- Price delta
        price - LAG(price, 1) OVER (
            PARTITION BY product_id, store_id ORDER BY snapshot_date
        ) AS price_delta_1d,

        -- Discount info
        discount_pct,
        old_price,
        CASE WHEN discount_pct IS NOT NULL AND discount_pct > 0 THEN 1 ELSE 0 END AS is_on_sale,

        -- Engagement
        rating,
        reviews,
        rating_status,

        -- Variant diagnostic — how many same-day listings existed
        variant_count,

        -- Calendar features
        EXTRACT(DOW  FROM snapshot_date)  AS day_of_week,
        EXTRACT(DAY  FROM snapshot_date)  AS day_of_month,
        EXTRACT(WEEK FROM snapshot_date)  AS week_of_year

    FROM daily_agg
)

SELECT * FROM with_features
ORDER BY product_name, seller, ds