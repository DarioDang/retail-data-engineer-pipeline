# 🛒 Retail Price Intelligence Pipeline

> An end-to-end data engineering pipeline that tracks electronics prices across New Zealand retailers daily — from raw API ingestion to an interactive analytics dashboard.

[![Pipeline Status](https://img.shields.io/badge/pipeline-automated-brightgreen)](https://app.prefect.cloud)
[![Dashboard](https://img.shields.io/badge/dashboard-live-blue)](https://digital-retail-dashboard.streamlit.app)
[![dbt](https://img.shields.io/badge/dbt-1.11-orange)](https://www.getdbt.com)
[![Python](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org)

---

## 📊 Live Dashboard

**[digital-retail-dashboard.streamlit.app](https://digital-retail-dashboard.streamlit.app)**

Tracks 8 consumer electronics products across 3 categories (Laptop, Phone, Camera) in the New Zealand market — updated daily.

---

## 🏗️ Architecture

```
SerpAPI (Google Shopping)
        ↓
  Ingestion (Python)
        ↓
  AWS S3 (Data Lake)
  Parquet files / daily partitions
        ↓
  AWS RDS PostgreSQL (Warehouse)
  raw_shopping.electronic_products
        ↓
  dbt Transformations
  staging → marts
        ↓
  Streamlit Dashboard
  Price trends · Seller intelligence · Deal finder
```

---

## ⚙️ Tech Stack

| Layer | Tool |
|---|---|
| **Data Source** | SerpAPI (Google Shopping) |
| **Ingestion** | Python + dlt (data load tool) |
| **Data Lake** | AWS S3 (Parquet, daily partitions) |
| **Warehouse** | AWS RDS PostgreSQL 15 |
| **Transformation** | dbt Core 1.11 |
| **Orchestration** | Prefect Cloud 3.x |
| **Dashboard** | Streamlit Community Cloud |
| **Infrastructure** | AWS (S3, RDS) |
| **Language** | Python 3.10 |

---

## 📁 Project Structure

```
retail-data-engineer-pipeline/
├── pipelines/
│   ├── ingest.py              # SerpAPI → S3
│   ├── load.py                # S3 → PostgreSQL via dlt
│   └── pipeline_flow.py       # Prefect flow orchestration
├── dbt/
│   └── retail_pipeline/
│       ├── models/
│       │   ├── staging/
│       │   │   └── stg_electronic_products.sql
│       │   └── marts/
│       │       ├── dim_product.sql
│       │       ├── dim_store.sql
│       │       ├── fact_price_snapshot.sql
│       │       ├── fact_price_changes.sql
│       │       ├── agg_category_summary.sql
│       │       └── agg_seller_per_product.sql
│       └── profiles.yml
├── dashboard/
│   ├── Home.py
│   ├── pages/
│   │   ├── 1_Overview.py
│   │   ├── 2_Price_Analysis.py
│   │   └── 3_Seller_Intelligence.py
│   └── utils/
│       ├── db.py
│       ├── queries.py
│       ├── sidebar.py
│       └── styles.py
└── requirements.txt
```

---

## 🔄 Pipeline Flow

The pipeline runs automatically every day at **8:00 PM NZST** via Prefect Cloud:

```
1. ingest.py     → Fetch 8 products × 40 results from SerpAPI → save Parquet to S3
2. load.py       → Load latest S3 Parquet → PostgreSQL (raw_shopping schema)
3. dbt run       → Transform raw → staging → marts (7 models)
4. dbt test      → Validate 25 data quality tests
5. Dashboard     → Auto-refreshes from PostgreSQL at 8pm NZT
```

---

## 📦 dbt Models

```
raw_shopping.electronic_products   ← source (dlt loaded)
        ↓
dev_staging.stg_electronic_products  ← cleaned, IQR outlier filtered, normalized
        ↓
dev_marts.dim_product              ← unique products
dev_marts.dim_store                ← unique sellers
dev_marts.fact_price_snapshot      ← all price records with surrogate keys
dev_marts.fact_price_changes       ← daily avg price per product (time series)
dev_marts.agg_category_summary     ← category-level aggregations
dev_marts.agg_seller_per_product   ← seller count and price stats per product
```

**Data Quality:**
- IQR outlier detection (3× IQR) with NZ market price floors
- Product name normalization across query variations
- 25 dbt tests covering not-null, unique, accepted values, relationships

---

## 📈 Dashboard Pages

| Page | Description |
|---|---|
| **Home** | Project overview, pipeline architecture diagram |
| **Overview** | Total listings, products, sellers, category summary |
| **Price Analysis** | Average price over time, best deals, price statistics insight cards, price spread |
| **Seller Intelligence** | Top rated sellers, cheapest seller per category |

---

## 🛍️ Products Tracked

| Category | Products |
|---|---|
| **Laptop** | Dell XPS 13, MacBook Air M3, HP Spectre x360 |
| **Phone** | iPhone 15, Samsung Galaxy S24, Samsung Galaxy A54 |
| **Camera** | GoPro Hero 13, DJI Osmo Action 5 |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- AWS account (S3 + RDS)
- SerpAPI key
- Prefect Cloud account

### Installation

```bash
git clone https://github.com/DarioDang/retail-data-engineer-pipeline.git
cd retail-data-engineer-pipeline
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:

```env
SERPAPI_KEY=your_serpapi_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=ap-southeast-2
POSTGRES_HOST=your_rds_endpoint
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=retail_warehouse
POSTGRES_PORT=5432
```

### Run Pipeline Manually

```bash
# Ingest only
python pipelines/ingest.py

# Full pipeline
python pipelines/pipeline_flow.py
```

### Run dbt

```bash
cd dbt/retail_pipeline
dbt run --target cloud
dbt test --target cloud
```

### Run Dashboard Locally

```bash
streamlit run dashboard/Home.py
```

---

## ☁️ Deployment

| Service | Platform | Cost |
|---|---|---|
| Dashboard | Streamlit Community Cloud | Free |
| Orchestration | Prefect Cloud | Free tier |
| Data Lake | AWS S3 | ~$0/month |
| Warehouse | AWS RDS (t4g.micro) | Free tier / ~$15/month after |

---

## 📊 Key Insights Delivered

- **Daily price tracking** across 8 products and 100+ sellers
- **Best deal finder** — cheapest seller per category updated daily
- **Price change alerts** — biggest price jumps/drops vs yesterday and last week
- **Seller intelligence** — top rated sellers, most competitive products
- **Historical trends** — average price over time with category grouping

---

## 👤 Author

**Dario Dang** — Data Analyst

[![GitHub](https://img.shields.io/badge/GitHub-DarioDang-black)](https://github.com/DarioDang)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-dario--dang-blue)](https://www.linkedin.com/in/dario-dang-89049020a/)
[![Portfolio](https://img.shields.io/badge/Portfolio-dariodang.github.io-orange)](https://dariodang.github.io)

---

