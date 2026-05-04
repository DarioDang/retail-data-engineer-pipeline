
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select avg_price
from "retail_pipeline"."dev_marts"."fact_price_changes"
where avg_price is null



  
  
      
    ) dbt_internal_test