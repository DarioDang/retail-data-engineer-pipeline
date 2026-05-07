{{
    config(
        materialized='table',
        -- When ready to switch: change to 'incremental'
        -- unique_key='record_id',
        -- incremental_strategy='merge'
    )
}}


-- Dimension: unique products in the basket 
WITH staging AS (
    SELECT DISTINCT 
        product_name,
        category
    FROM {{ ref('stg_electronic_products') }}
)

SELECT 
    {{dbt_utils.generate_surrogate_key(['product_name'])}} AS product_id,
    product_name,
    category
FROM staging
ORDER BY category, product_name 
