-- Staging model: clean and normalize raw data from Postgres -- 
-- Source : raw_shopping.electronic_products (loaded by dlt)
-- Outlier detection: IQR method (3x IQR for conservative filtering)

-- Price floor reasoning (NZ market):
-- laptop: NZD 500  — minimum for new laptop (used/refurbished excluded by design)
-- phone:  NZD 200  — minimum for new smartphone
-- camera: NZD 300  — minimum for new action camera (GoPro/DJI)
-- Note: this pipeline tracks new retail prices only
-- used/refurbished listings are excluded intentionally

WITH source AS (
    SELECT *
    FROM {{ source('raw_shopping', 'electronic_products') }}
    WHERE
        price IS NOT NULL
        AND product_name IS NOT NULL
        AND seller IS NOT NULL
),

iqr_calc AS (
    SELECT
        LOWER(TRIM(category))                                           AS category,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY price)            AS q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY price)            AS q3
    FROM source
    GROUP BY LOWER(TRIM(category))
),

iqr_bounds AS (
    SELECT
        category,
        q1,
        q3,
        GREATEST(
            q1 - 3.0 * (q3 - q1),
            CASE
                WHEN category = 'laptop' THEN 500.0
                WHEN category = 'phone'  THEN 200.0
                WHEN category = 'camera' THEN 300.0
                ELSE 10.0
            END
        )                           AS lower_bound,
        q3 + 3.0 * (q3 - q1)       AS upper_bound
    FROM iqr_calc
),

flagged AS (
    SELECT
        s.*,
        b.lower_bound,
        b.upper_bound,
        CASE WHEN s.price > b.upper_bound THEN true ELSE false END AS is_price_too_high,
        CASE WHEN s.price < b.lower_bound THEN true ELSE false END AS is_price_too_low
    FROM source s
    LEFT JOIN iqr_bounds b
        ON LOWER(TRIM(s.category)) = b.category
),

cleaned AS (
    SELECT
        -- Identifiers
        _dlt_id                         AS record_id,
        product_id,

        -- Product details
        TRIM(product_name)              AS product_name,
        LOWER(TRIM(category))           AS category,
        TRIM(title)                     AS title,

        -- Pricing
        ROUND(price::numeric, 2)        AS price,
        ROUND(old_price::numeric, 2)    AS old_price,

        -- Discount calculation
        CASE
            WHEN old_price IS NOT NULL AND old_price > 0
            THEN ROUND(((old_price - price) / old_price * 100)::numeric, 2)
            ELSE NULL
        END AS discount_pct,

        -- Seller info
        TRIM(seller)                    AS seller,

        -- Ratings
        ROUND(rating::numeric, 1)       AS rating,
        COALESCE(reviews::integer, 0)   AS reviews,
        position::integer               AS position,

        -- Rating flag
        CASE
            WHEN rating IS NOT NULL THEN true
            ELSE false
        END AS has_rating,

        -- Competition: true if multiple sellers offer this product
        COALESCE(multiple_sources::boolean, false)  AS multiple_sources,

        -- Condition: standardised to lowercase, null = new item
        LOWER(TRIM(second_hand_condition))          AS condition,

        -- Derived: clean boolean for new vs used
        CASE
            WHEN second_hand_condition IS NULL THEN true
            ELSE false
        END  AS is_new_condition,

        -- IQR bounds for auditing
        ROUND(lower_bound::numeric, 2)  AS price_lower_bound,
        ROUND(upper_bound::numeric, 2)  AS price_upper_bound,
        is_price_too_high,
        is_price_too_low,

        -- Timestamps
        DATE_TRUNC('second', ingested_at::timestamp with time zone) AS ingested_at,
        DATE(ingested_at AT TIME ZONE 'Pacific/Auckland')           AS snapshot_date

    FROM flagged
    WHERE
        is_price_too_high = false
        AND is_price_too_low = false
)

-- ── Product name normalization ─────────────────────────────────────────────
-- Maps product name variations to canonical names
-- Add new mappings here whenever a product query changes
normalized AS (
    SELECT
        *,
        CASE
            -- DJI Osmo Action variants → canonical name
            WHEN LOWER(product_name) LIKE '%dji osmo action%' THEN 'DJI Osmo Action'
            -- GoPro variants (future proofing)
            WHEN LOWER(product_name) LIKE '%gopro hero%'      THEN 'GoPro Hero 13'
            -- iPhone variants (future proofing)
            WHEN LOWER(product_name) LIKE '%iphone 15%'       THEN 'iPhone 15'
            -- Samsung variants (future proofing)
            WHEN LOWER(product_name) LIKE '%galaxy s24%'      THEN 'Samsung Galaxy S24'
            WHEN LOWER(product_name) LIKE '%galaxy a54%'      THEN 'Samsung Galaxy A54'
            -- MacBook variants (future proofing)
            WHEN LOWER(product_name) LIKE '%macbook air m3%'  THEN 'MacBook Air M3'
            -- Dell variants (future proofing)
            WHEN LOWER(product_name) LIKE '%dell xps 13%'     THEN 'Dell XPS 13'
            -- HP variants (future proofing)
            WHEN LOWER(product_name) LIKE '%hp spectre%'      THEN 'HP Spectre x360'
            -- Default — keep original
            ELSE product_name
        END AS product_name_normalized
    FROM cleaned
)

SELECT
    record_id,
    product_id,
    product_name_normalized     AS product_name,  -- ← use normalized name
    category,
    title,
    price,
    old_price,
    discount_pct,
    seller,
    rating,
    reviews,
    position,
    has_rating,
    multiple_sources,
    condition,
    is_new_condition,
    price_lower_bound,
    price_upper_bound,
    is_price_too_high,
    is_price_too_low,
    ingested_at,
    snapshot_date
FROM normalized