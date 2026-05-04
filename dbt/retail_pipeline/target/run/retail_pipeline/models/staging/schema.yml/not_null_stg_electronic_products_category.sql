
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select category
from "retail_pipeline"."dev_staging"."stg_electronic_products"
where category is null



  
  
      
    ) dbt_internal_test