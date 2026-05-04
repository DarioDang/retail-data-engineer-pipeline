-- Dimension: unique sellers/stores
WITH staging AS (
    SELECT DISTINCT seller
    FROM "retail_pipeline"."dev_staging"."stg_electronic_products"
    WHERE seller IS NOT NULL
)

SELECT 
    md5(cast(coalesce(cast(seller as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) AS store_id,
    seller AS store_name
FROM staging
ORDER BY store_name