-- Dimension: unique products in the basket 
WITH staging AS (
    SELECT DISTINCT 
        product_name,
        category
    FROM "retail_pipeline"."dev_staging"."stg_electronic_products"
)

SELECT 
    md5(cast(coalesce(cast(product_name as TEXT), '_dbt_utils_surrogate_key_null_') as TEXT)) AS product_id,
    product_name,
    category
FROM staging
ORDER BY category, product_name