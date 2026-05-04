
  create view "retail_pipeline"."dev_staging"."stg_electronic_products__dbt_tmp"
    
    
  as (
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
    FROM "retail_pipeline"."raw_shopping"."electronic_products"
    WHERE
        price IS NOT NULL
        AND product_name IS NOT NULL
        AND seller IS NOT NULL
),

-- Step 1: Calculate Q1 and Q3 per category using GROUP BY
iqr_calc AS (
    SELECT
        LOWER(TRIM(category))                                           AS category,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY price)            AS q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY price)            AS q3
    FROM source
    GROUP BY LOWER(TRIM(category))
),

-- Step 2: Calculate bounds
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

-- Step 3: Join bounds back to source
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

-- Step 4: Clean and filter
cleaned AS (
    SELECT
        -- Identifiers
        _dlt_id AS record_id,

        -- Product details
        TRIM(product_name)      AS product_name,
        LOWER(TRIM(category))   AS category,
        TRIM(title)             AS title,

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
        TRIM(seller) AS seller,

        -- Ratings
        ROUND(rating::numeric, 1)       AS rating,
        COALESCE(reviews::integer, 0)   AS reviews,
        position::integer               AS position,

        -- Rating flag
        CASE
            WHEN rating IS NOT NULL THEN true
            ELSE false
        END AS has_rating,

        -- IQR bounds for auditing
        ROUND(lower_bound::numeric, 2)  AS price_lower_bound,
        ROUND(upper_bound::numeric, 2)  AS price_upper_bound,
        is_price_too_high,
        is_price_too_low,

        -- Timestamps
        DATE_TRUNC('second', ingested_at::timestamp with time zone) AS ingested_at,
        DATE(ingested_at AT TIME ZONE 'Pacific/Auckland')  AS snapshot_date

    FROM flagged
    WHERE
        is_price_too_high = false
        AND is_price_too_low = false
)

SELECT * FROM cleaned
  );