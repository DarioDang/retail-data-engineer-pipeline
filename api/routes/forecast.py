# api/routes/forecast.py
import pandas as pd
from fastapi import APIRouter, HTTPException
from api.db import run_query, engine
from api import queries
from sqlalchemy import text

router = APIRouter()


@router.get("/products")
def get_forecast_products():
    df = run_query(queries.FORECAST_PRODUCTS)
    return df["product_name"].tolist()


@router.get("/summary")
def get_forecast_summary():
    df = run_query(queries.FORECAST_SUMMARY)
    return df.to_dict(orient="records")


@router.get("/{product_name}/best")
def get_best_seller_forecast(product_name: str):
    with engine.connect() as conn:
        df = pd.read_sql(
            text(queries.FORECAST_BEST_SELLER),
            conn,
            params={"product_name": product_name}
        )
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No forecast found for product: {product_name}"
        )
    return df.iloc[0].to_dict()


@router.get("/{product_name}")
def get_forecast_by_product(product_name: str):
    with engine.connect() as conn:
        df = pd.read_sql(
            text(queries.FORECAST_BY_PRODUCT),
            conn,
            params={"product_name": product_name}
        )
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No forecast data found for product: {product_name}"
        )
    return df.to_dict(orient="records")