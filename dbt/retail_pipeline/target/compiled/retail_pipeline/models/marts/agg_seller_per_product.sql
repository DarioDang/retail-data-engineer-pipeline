-- Aggregation: seller count and price stats per product
WITH base AS (
    SELECT
        product_name,
        category,
        seller,
        price
    FROM "retail_pipeline"."dev_marts"."fact_price_snapshot"
),

stats AS (
    SELECT
        product_name,
        category,
        COUNT(DISTINCT seller)              AS seller_count,
        ROUND(MIN(price)::numeric, 2)       AS min_price,
        ROUND(MAX(price)::numeric, 2)       AS max_price,
        ROUND(AVG(price)::numeric, 2)       AS avg_price,
        ROUND(STDDEV(price)::numeric, 2)    AS price_stddev
    FROM base
    GROUP BY product_name, category
),

cheapest AS (
    -- Get cheapest seller per product
    SELECT DISTINCT ON (product_name)
        product_name,
        seller AS cheapest_seller,
        price  AS cheapest_price
    FROM base
    ORDER BY product_name, price ASC
)

SELECT
    s.product_name,
    s.category,
    s.seller_count,
    s.min_price,
    s.max_price,
    s.avg_price,
    s.price_stddev,
    c.cheapest_seller,
    c.cheapest_price
FROM stats s
LEFT JOIN cheapest c ON s.product_name = c.product_name
ORDER BY s.category, s.product_name