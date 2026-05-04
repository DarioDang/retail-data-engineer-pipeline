## ---- SECTION 01 : import & config ---- ##
import os 
import dlt 
import serpapi
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

### Setup logging 
load_dotenv()

logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
COUNTRY_CODE = "nz"
NUM_RESULTS = 40 # full basket for real pipelines 

client = serpapi.Client(api_key=SERPAPI_KEY)

## ---- SECTION 02 : PRODUCT BASKET ---- ##
PRODUCTS = [
    {"name": "Dell XPS 13",            "query": "Dell XPS 13 laptop",          "category": "laptops"},
    {"name": "MacBook Air M3",         "query": "Apple MacBook Air M3",        "category": "laptop"},
    {"name": "HP Spectre x360",        "query": "HP Spectre x360 laptop",      "category": "laptop"},
    {"name": "iPhone 15",              "query": "Apple iPhone 15 smartphone",  "category": "phone"},
    {"name": "Samsung Galaxy S24",     "query": "Samsung Galaxy S24 phone",    "category": "phone"},
    {"name": "Samsung Galaxy A54",     "query": "Samsung Galaxy A54 phone",    "category": "phone"},
    {"name": "GoPro Hero 13",          "query": "GoPro Hero 13 action camera", "category": "camera"},
    {"name": "DJI Osmo Action",        "query": "DJI Osmo Action camera",      "category": "camera"},
]

## ---- SECTION 03 : FETCH FUNCTION  ---- ##
### We wrap in try/except so one failed API call doesn't crash the entire pipeline run. ###
def fetch_product(query: str, num_results: int = NUM_RESULTS) -> list[dict]:
    """ Fetch raw shopping results from SERPAPI for a single product query."""

    try:
        results = client.search({
            "engine": "google_shopping",
            "q" : query,
            "gl": COUNTRY_CODE,
            "hl": "en"
        })

        shopping = results.get("shopping_results", [])[:num_results]
        logger.info(f"Fetched {len(shopping)} results for: {query}")
        return shopping 

    except Exception as e:
        logger.error(f"Failed to fetch '{query}': {e}")
        return []

## ---- SECTION 04 : PARSED FUNCTION  ---- ##
def parse_product(result: dict, category: str, product_name: str) -> dict:
    """ Extract and normalize fields from a raw SERPAPI shopping result."""
    return {
        "product_name": product_name,
        "category":     category,
        "title":        result.get("title"),
        "price":        result.get("extracted_price"),
        "old_price":    float(result["extracted_old_price"]) if result.get("extracted_old_price") else None,
        "seller":       result.get("source"),
        "rating":       float(result["rating"]) if result.get("rating") else None,
        "reviews":      int(result["reviews"]) if result.get("reviews") else None,
        "position":     int(result["position"]) if result.get("position") else None,
        "ingested_at":  datetime.now(timezone.utc).isoformat(),
    }

## ---- SECTION 05 : DLT RESOURCE  ---- ##
@dlt.resource(
    name="shopping_results",
    write_disposition="append",
    columns={
        "old_price": {"data_type": "double"},  
    }
)

def shopping_resource():
    for product in PRODUCTS:  
        logger.info(f"Processing: {product['name']}")
        raw_results = fetch_product(product["query"])
        for result in raw_results:
            yield parse_product(result, product["category"], product["name"])

## ---- SECTION 06 : MAIN PIPELINE RUN  ---- ##
def run_pipeline():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    bucket_url = (
        f"s3://{os.getenv('AWS_BUCKET_NAME')}"
        f"/raw/shopping/{today}"
    )

    pipeline = dlt.pipeline(
        pipeline_name="retail_price_intelligence",
        destination=dlt.destinations.filesystem(
            bucket_url=bucket_url,
            credentials={"region_name": os.getenv("AWS_REGION")}
        ),
        dataset_name="shopping_results"
    )

    logger.info("Starting pipeline run...")
    load_info = pipeline.run(shopping_resource())
    logger.info(f"Pipeline complete: {load_info}")

    return load_info


if __name__ == "__main__":
    run_pipeline()