```bash
dbt run --select stg_electronic_products.sql --profiles-dir .

dbt run --select dim_product --profiles-dir .

dbt run --select dim_store --profiles-dir .

dbt run --select fact_price_snapshot.sql --profiles-dir .

dbt run --select agg_seller_per_product.sql --profiles-dir .

dbt run --select agg_category_summary.sql --profiles-dir .
```

