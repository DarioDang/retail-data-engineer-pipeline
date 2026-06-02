{{
    config(
        materialized='table',
    )
}}

-- ML training table: one row per product per seller per day
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
        CASE WHEN discount_pct IS NOT NULL THEN 1 ELSE 0 END AS is_on_sale,

        -- Engagement
        rating,
        reviews,
        rating_status,

        -- Calendar features
        EXTRACT(DOW  FROM snapshot_date)  AS day_of_week,
        EXTRACT(DAY  FROM snapshot_date)  AS day_of_month,
        EXTRACT(WEEK FROM snapshot_date)  AS week_of_year

    FROM base
)

SELECT * FROM with_features
ORDER BY product_name, seller, ds
