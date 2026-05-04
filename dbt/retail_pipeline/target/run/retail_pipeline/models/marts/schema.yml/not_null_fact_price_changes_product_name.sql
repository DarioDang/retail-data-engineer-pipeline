
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select product_name
from "retail_pipeline"."dev_marts"."fact_price_changes"
where product_name is null



  
  
      
    ) dbt_internal_test