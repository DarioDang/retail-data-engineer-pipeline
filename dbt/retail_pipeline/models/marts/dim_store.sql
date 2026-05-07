{{
    config(
        materialized='table',
        -- When ready to switch: change to 'incremental'
        -- unique_key='record_id',
        -- incremental_strategy='merge'
    )
}}

-- Dimension: unique sellers/stores
WITH staging AS (
    SELECT DISTINCT seller
    FROM {{ ref('stg_electronic_products') }}
    WHERE seller IS NOT NULL
)

SELECT 
    {{dbt_utils.generate_surrogate_key(['seller'])}} AS store_id,
    seller AS store_name
FROM staging
ORDER BY store_name

