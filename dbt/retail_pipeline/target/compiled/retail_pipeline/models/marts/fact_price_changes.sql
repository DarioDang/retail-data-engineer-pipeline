-- Fact table: day - over - day price changes per product per seller --
WITH daily_avg AS (
    SELECT 
        snapshot_date,
        product_name,
        category,
        ROUND(AVG(price)::numeric, 2) AS avg_price
    FROM "retail_pipeline"."dev_marts"."fact_price_snapshot"
    GROUP BY snapshot_date, product_name, category
),

with_changes AS (
    SELECT
        snapshot_date,
        product_name,
        category,
        avg_price,

        -- Previous day price
        LAG(avg_price) OVER (
            PARTITION BY product_name
            ORDER BY snapshot_date
        ) AS prev_day_price,

        -- Price change amount
        ROUND(
            (avg_price - LAG(avg_price) OVER (
                PARTITION BY product_name
                ORDER BY snapshot_date
            ))::numeric, 2
        ) AS price_change,

        -- Price change percentage
        ROUND(
            ((avg_price - LAG(avg_price) OVER (
                PARTITION BY product_name
                ORDER BY snapshot_date
            )) / NULLIF(LAG(avg_price) OVER (
                PARTITION BY product_name
                ORDER BY snapshot_date
            ), 0) * 100)::numeric, 2
        ) AS price_change_pct

    FROM daily_avg
)

SELECT 
    snapshot_date,
    product_name,
    category,
    avg_price,
    prev_day_price,
    price_change,
    price_change_pct,

    CASE 
        WHEN price_change > 0 THEN 'increased'
        WHEN price_change < 0 THEN 'decreased'
        WHEN price_change = 0 THEN 'stable'
        ELSE 'no_comparision'
    END AS price_trend

FROM with_changes
ORDER BY product_name, snapshot_date