
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select record_id
from "retail_pipeline"."dev_marts"."fact_price_snapshot"
where record_id is null



  
  
      
    ) dbt_internal_test