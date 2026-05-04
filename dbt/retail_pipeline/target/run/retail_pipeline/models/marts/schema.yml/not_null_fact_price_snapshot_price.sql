
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select price
from "retail_pipeline"."dev_marts"."fact_price_snapshot"
where price is null



  
  
      
    ) dbt_internal_test