
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select seller
from "retail_pipeline"."dev_staging"."stg_electronic_products"
where seller is null



  
  
      
    ) dbt_internal_test