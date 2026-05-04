
    
    

select
    store_id as unique_field,
    count(*) as n_records

from "retail_pipeline"."dev_marts"."dim_store"
where store_id is not null
group by store_id
having count(*) > 1


