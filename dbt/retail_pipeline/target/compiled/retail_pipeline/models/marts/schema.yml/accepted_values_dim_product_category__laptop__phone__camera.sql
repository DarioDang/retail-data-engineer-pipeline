
    
    

with all_values as (

    select
        category as value_field,
        count(*) as n_records

    from "retail_pipeline"."dev_marts"."dim_product"
    group by category

)

select *
from all_values
where value_field not in (
    'laptop','phone','camera'
)


