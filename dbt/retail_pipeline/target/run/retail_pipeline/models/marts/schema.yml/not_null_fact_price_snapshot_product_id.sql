
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select product_id
from "retail_pipeline"."dev_marts"."fact_price_snapshot"
where product_id is null



  
  
      
    ) dbt_internal_test