-- Aggregation: summary stats per category
SELECT
    category,
    COUNT(DISTINCT product_name) AS product_count,
    COUNT(DISTINCT seller) AS seller_count,
    COUNT(*) AS total_listings,
    ROUND(MIN(price)::numeric, 2) AS min_price,
    ROUND(MAX(price)::numeric, 2) AS max_price,
    ROUND(AVG(price)::numeric, 2) AS avg_price

FROM "retail_pipeline"."dev_marts"."fact_price_snapshot"
GROUP BY category
ORDER BY category