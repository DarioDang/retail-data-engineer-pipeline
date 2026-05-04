
    
    

select
    record_id as unique_field,
    count(*) as n_records

from "retail_pipeline"."dev_marts"."fact_price_snapshot"
where record_id is not null
group by record_id
having count(*) > 1


