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

        -- Derived: clean boolean for new vs used, from the structured field
        CASE
            WHEN second_hand_condition IS NULL THEN true
            ELSE false
        END  AS is_new_condition,

        -- Title-based condition detection — second_hand_condition is not
        -- reliably populated by SerpAPI for all sellers. Many refurbished/
        -- used listings only signal their condition in the title text
        -- (e.g. "iPhone 15 128GB Pink Refurbished Excellent Grade"),
        -- with second_hand_condition left NULL. This catches those.
        CASE
            WHEN LOWER(title) LIKE '%refurbished%'
                 OR LOWER(title) LIKE '%a grade%'
                 OR LOWER(title) LIKE '%b grade%'
                 OR LOWER(title) LIKE '%like new%'
                 OR LOWER(title) LIKE '%excellent grade%'
                 OR LOWER(title) LIKE '%good grade%'
                 OR LOWER(title) LIKE '%open box%'
                 OR LOWER(title) LIKE '%renewed%'
                 OR LOWER(title) LIKE '%pre-owned%'
                 OR LOWER(title) LIKE '%preowned%'
                 OR LOWER(title) LIKE '%used%'
                THEN true
            ELSE false
        END AS is_used_or_refurb_title,

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
),

-- ── Product name normalization ─────────────────────────────────────────────
-- Maps listings to canonical product names based on the ACTUAL LISTING TITLE,
-- not the SerpAPI search query (product_name). This is critical: SerpAPI's
-- "related products" matching can return a different model/generation/brand
-- under the same search query (e.g. searching "DJI Osmo Action" can return
-- "DJI Osmo Action 5 Pro", "DJI Osmo Pocket 3", or even unrelated products).
--
-- Each rule requires the title to confidently identify the exact tracked
-- product/generation, and explicitly excludes known contaminant patterns
-- (other generations, other product lines, accessories, wrong brands,
-- and higher/lower SKU tiers like Pro/Pro Max/Ultra).
--
-- Rows that don't confidently match any tracked product are dropped (see
-- final WHERE clause) rather than mislabeled under the wrong product.
normalized AS (
    SELECT
        *,
        CASE
            -- DJI Osmo Action — exclude other Osmo generations/lines
            WHEN LOWER(title) LIKE '%osmo action%'
                 AND LOWER(title) NOT LIKE '%osmo action 4%'
                 AND LOWER(title) NOT LIKE '%osmo action 5%'
                 AND LOWER(title) NOT LIKE '%osmo action 6%'
                 AND LOWER(title) NOT LIKE '%pocket%'
                 AND LOWER(title) NOT LIKE '%360%'
                THEN 'DJI Osmo Action'

            -- GoPro Hero 13 — exclude other GoPro lines/accessories
            WHEN (LOWER(title) LIKE '%hero 13%' OR LOWER(title) LIKE '%hero13%')
                 AND LOWER(title) NOT LIKE '%max%'
                 AND LOWER(title) NOT LIKE '%lens%'
                 AND LOWER(title) NOT LIKE '%hero 9-13%'
                 AND LOWER(title) NOT LIKE '%hero9-13%'
                THEN 'GoPro Hero 13'

            -- iPhone 15 — base model only, exclude Pro/Pro Max/Plus tiers
            WHEN LOWER(title) LIKE '%iphone 15%'
                 AND LOWER(title) NOT LIKE '%iphone 15 pro%'
                 AND LOWER(title) NOT LIKE '%iphone 15 plus%'
                THEN 'iPhone 15'

            -- Samsung Galaxy S24 — exclude Ultra/Plus variants
            WHEN LOWER(title) LIKE '%galaxy s24%'
                 AND LOWER(title) NOT LIKE '%s24 ultra%'
                 AND LOWER(title) NOT LIKE '%s24+%'
                 AND LOWER(title) NOT LIKE '%s24 plus%'
                THEN 'Samsung Galaxy S24'

            -- Samsung Galaxy A54 — exclude wrong-brand contamination (e.g. OPPO A54)
            WHEN LOWER(title) LIKE '%galaxy a54%'
                 AND LOWER(title) NOT LIKE '%oppo%'
                THEN 'Samsung Galaxy A54'

            -- MacBook Air M3 — exclude other chip generations and MacBook Pro
            WHEN LOWER(title) LIKE '%macbook air%'
                 AND LOWER(title) LIKE '%m3%'
                 AND LOWER(title) NOT LIKE '%macbook pro%'
                 AND LOWER(title) NOT LIKE '%m1%'
                 AND LOWER(title) NOT LIKE '%m2%'
                 AND LOWER(title) NOT LIKE '%m4%'
                 AND LOWER(title) NOT LIKE '%m5%'
                THEN 'MacBook Air M3'

            -- Dell XPS 13 — exclude XPS 13 Plus (different model line)
            WHEN LOWER(title) LIKE '%dell xps 13%'
                 AND LOWER(title) NOT LIKE '%xps 13 plus%'
                THEN 'Dell XPS 13'

            -- HP Spectre x360 — require both "spectre" and "x360"
            WHEN LOWER(title) LIKE '%hp spectre%'
                 AND LOWER(title) LIKE '%x360%'
                THEN 'HP Spectre x360'

            -- No confident match — drop via WHERE clause below
            ELSE NULL
        END AS product_name_normalized
    FROM cleaned
)

SELECT
    record_id,
    product_id,
    product_name_normalized  AS product_name,
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
    is_used_or_refurb_title,
    price_lower_bound,
    price_upper_bound,
    is_price_too_high,
    is_price_too_low,
    ingested_at,
    snapshot_date
FROM normalized
WHERE
    product_name_normalized IS NOT NULL    -- drop rows that don't confidently match a tracked product
    AND is_used_or_refurb_title = false    -- drop refurbished/used listings detected via title