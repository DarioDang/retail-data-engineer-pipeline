{{
    config(
        materialized='table',
        -- When ready to switch: change to 'incremental'
        -- unique_key='record_id',
        -- incremental_strategy='merge'
    )
}}


-- Fact table: daily price snapshot for each product per seller
WITH staging AS (
    SELECT 
        record_id,
        product_name,
        category,
        title,
        price,
        old_price,
        discount_pct,
        seller,
        rating,
        reviews,
        has_rating,
        position,
        ingested_at,
        snapshot_date      
    FROM {{ ref('stg_electronic_products') }}
),

product AS (
    SELECT 
        product_id,
        product_name,
        category
    FROM {{ ref('dim_product') }}
),

stores AS (
    SELECT 
        store_id,
        store_name
    FROM {{ ref('dim_store') }}
)

SELECT 
    -- Keys
    stg.record_id,
    p.product_id,
    s.store_id,

    -- Snapshot info
    stg.snapshot_date,
    stg.ingested_at,

    -- Product info
    stg.product_name,
    stg.category,
    stg.title,
    stg.position,

    -- Pricing
    stg.price,
    stg.old_price,
    stg.discount_pct,

    -- Store
    stg.seller,

    -- Engagement
    stg.rating,
    stg.reviews,
    stg.has_rating,

    -- Rating reliability indicator
    CASE
        WHEN stg.rating IS NOT NULL AND stg.reviews >= 10 THEN 'verified'
        WHEN stg.rating IS NOT NULL AND stg.reviews < 10  THEN 'limited'
        ELSE 'unrated'
    END AS rating_status

FROM staging AS stg 
LEFT JOIN product AS p
    ON stg.product_name = p.product_name
LEFT JOIN stores AS s
    ON stg.seller = s.store_name
ORDER BY stg.snapshot_date DESC, stg.product_name 