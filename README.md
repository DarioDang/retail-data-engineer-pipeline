# 🛒 Retail Price Intelligence Pipeline

> An end-to-end data engineering pipeline that tracks electronics prices across New Zealand retailers daily — from raw API ingestion to an interactive analytics dashboard.

[![Pipeline Status](https://img.shields.io/badge/pipeline-automated-brightgreen)](https://app.prefect.cloud)
[![Live Dashboard](https://img.shields.io/badge/dashboard-live-blue)](https://retail-price-intelligence.netlify.app)
[![API](https://img.shields.io/badge/API-live-success)](https://retail-price-api.onrender.com/docs)
[![dbt](https://img.shields.io/badge/dbt-1.11-orange)](https://www.getdbt.com)
[![Python](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org)

---

## 🌐 Live Links

| Service | URL |
|---|---|
| **HTML Dashboard** | [retail-price-intelligence.netlify.app](https://retail-price-intelligence.netlify.app) |
| **FastAPI Backend** | [retail-price-api.onrender.com/docs](https://retail-price-api.onrender.com/docs) |
| **Streamlit Dashboard** | [digital-retail-dashboard.streamlit.app](https://digital-retail-dashboard.streamlit.app) |

---

## 📸 Dashboard Preview

> Tracks 8 consumer electronics products across 3 categories (Laptop, Phone, Camera) in the New Zealand market — updated daily at 8PM NZST.

---

## 🏗️ Architecture

```
SerpAPI (Google Shopping)
        ↓
  Python Ingestion (dlt)
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
  ┌─────────────────────────┐    ┌──────────────────────────────┐
  │   FastAPI Backend        │    │   Streamlit Dashboard         │
  │   (Render)               │    │   (Streamlit Community Cloud) │
  └────────┬────────────────┘    └──────────────────────────────┘
           │
  HTML/CSS/JS Frontend
  (Netlify)
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
| **API Backend** | FastAPI + SQLAlchemy (Render) |
| **HTML Dashboard** | HTML / CSS / JS + Plotly.js (Netlify) |
| **Streamlit Dashboard** | Streamlit Community Cloud |
| **Monitoring** | UptimeRobot |
| **Language** | Python 3.10 |

---

## 📁 Project Structure

```
retail-data-engineer-pipeline/
├── pipelines/
│   ├── ingest.py                   # SerpAPI → S3
│   ├── load.py                     # S3 → PostgreSQL via dlt
│   └── pipeline_flow.py            # Prefect flow orchestration
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
├── api/                            # FastAPI backend
│   ├── main.py                     # App entry point + CORS
│   ├── db.py                       # SQLAlchemy engine
│   ├── queries.py                  # All SQL queries
│   ├── cache.py                    # TTL cache (resets 8PM NZT)
│   ├── routes/
│   │   ├── overview.py             # /api/overview/* endpoints
│   │   ├── price.py                # /api/price/* endpoints
│   │   └── seller.py              # /api/seller/* endpoints
│   └── requirements.txt
├── frontend/                       # HTML/CSS/JS dashboard
│   ├── index.html                  # Home page
│   ├── overview.html               # Overview dashboard
│   ├── price.html                  # Price analysis
│   ├── seller.html                 # Seller intelligence
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── api.js                  # API fetch layer
│   │   ├── overview.js
│   │   ├── price.js
│   │   └── seller.js
│   └── static/                     # Icons and images
├── dashboard/                      # Streamlit dashboard (legacy)
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
├── render.yaml                     # Render deployment config
├── .python-version                 # Python 3.10.0
└── requirements.txt
```

---

## 🔄 Pipeline Flow

The pipeline runs automatically every day at **8:00 PM NZST** via Prefect Cloud:

```
1. ingest.py       → Fetch 8 products × 40 results from SerpAPI → save Parquet to S3
2. load.py         → Load latest S3 Parquet → PostgreSQL (raw_shopping schema)
3. dbt run         → Transform raw → staging → marts (7 models)
4. dbt test        → Validate 25 data quality tests
5. API cache reset → FastAPI cache expires at 8PM NZT, fresh data served
6. Dashboard       → HTML dashboard pulls fresh data from FastAPI
```

---

## 📦 dbt Models

```
raw_shopping.electronic_products       ← source (dlt loaded)
        ↓
dev_staging.stg_electronic_products    ← cleaned, IQR outlier filtered, normalized
        ↓
dev_marts.dim_product                  ← unique products
dev_marts.dim_store                    ← unique sellers
dev_marts.fact_price_snapshot          ← all price records with surrogate keys
dev_marts.fact_price_changes           ← daily avg price per product (time series)
dev_marts.agg_category_summary         ← category-level aggregations
dev_marts.agg_seller_per_product       ← seller count and price stats per product
```

**Data Quality:**
- IQR outlier detection (3× IQR) with NZ market price floors
- Product name normalization across query variations
- 25 dbt tests covering not-null, unique, accepted values, relationships

---

## 🌐 API Endpoints

The FastAPI backend exposes 18 endpoints across 3 routers:

| Router | Endpoint | Description |
|---|---|---|
| **Overview** | `GET /api/overview/total-listings` | Total listing count |
| | `GET /api/overview/total-products` | Total product count |
| | `GET /api/overview/total-sellers` | Total seller count |
| | `GET /api/overview/listings-by-category` | Listings per category |
| | `GET /api/overview/category-summary` | Category stats table |
| | `GET /api/overview/last-updated` | Last pipeline run date |
| **Price** | `GET /api/price/avg-price-over-time` | Daily avg price per product |
| | `GET /api/price/stats-per-product` | Price stats per product |
| | `GET /api/price/price-range-by-product` | Raw prices for box plots |
| | `GET /api/price/discounts` | All discounted listings |
| | `GET /api/price/change-vs-yesterday` | Price change % vs yesterday |
| | `GET /api/price/change-vs-last-week` | Price change % vs last week |
| | `GET /api/price/stats-last-7-days` | 7-day price statistics |
| **Seller** | `GET /api/seller/seller-count-per-product` | Seller count per product |
| | `GET /api/seller/cheapest-seller-per-product` | Best deal per product |
| | `GET /api/seller/rating-by-seller` | Top sellers by rating |
| | `GET /api/seller/rating-status-distribution` | Rating status breakdown |
| | `GET /api/seller/cheapest-seller-per-category` | Cheapest seller per category |

Interactive API docs: [retail-price-api.onrender.com/docs](https://retail-price-api.onrender.com/docs)

---

## 📈 Dashboard Pages

### HTML Dashboard (Netlify + FastAPI)

| Page | Description |
|---|---|
| **Home** | Project overview, pipeline architecture, navigation guide |
| **Overview** | KPI cards, category summary, listings distribution, avg price trend |
| **Price Analysis** | Best deals, per-product price charts, box plots, insight carousel, price spread |
| **Seller Intelligence** | Seller count chart, rating distribution, trust bubble chart, reputation scorecard |

### Streamlit Dashboard (Legacy)

| Page | Description |
|---|---|
| **Home** | Project overview and pipeline diagram |
| **Overview** | Total listings, products, sellers, category summary |
| **Price Analysis** | Average price over time, best deals, price statistics |
| **Seller Intelligence** | Top rated sellers, cheapest seller per category |

---

## 🛍️ Products Tracked

| Category | Products |
|---|---|
| **Laptop** | Dell XPS 13, MacBook Air M3, HP Spectre x360 |
| **Phone** | iPhone 15, Samsung Galaxy S24, Samsung Galaxy A54 |
| **Camera** | GoPro Hero 13, DJI Osmo Action |

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

Create a `.env` file in the project root:

```env
# SerpAPI
SERPAPI_KEY=your_serpapi_key

# AWS
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=ap-southeast-2

# PostgreSQL (AWS RDS)
POSTGRES_HOST=your_rds_endpoint
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=retail_warehouse
POSTGRES_PORT=5432
```

### Run Pipeline Manually

```bash
# Full pipeline
python pipelines/pipeline_flow.py

# Ingestion only
python pipelines/ingest.py
```

### Run dbt Transformations

```bash
cd dbt/retail_pipeline
dbt run --target cloud
dbt test --target cloud
```

### Run FastAPI Backend Locally

```bash
uvicorn api.main:app --reload --port 8000
# API docs at http://localhost:8000/docs
```

### Run HTML Dashboard Locally

```bash
cd frontend
python3 -m http.server 3000
# Open http://localhost:3000/overview.html
```

### Run Streamlit Dashboard Locally

```bash
streamlit run dashboard/Home.py
```

---

## ☁️ Deployment

| Service | Platform | Cost |
|---|---|---|
| **HTML Dashboard** | Netlify | Free |
| **FastAPI Backend** | Render (free tier) | Free |
| **Streamlit Dashboard** | Streamlit Community Cloud | Free |
| **Orchestration** | Prefect Cloud | Free tier |
| **Data Lake** | AWS S3 | ~$0/month |
| **Warehouse** | AWS RDS (t4g.micro) | Free tier / ~$15/month after |
| **Uptime Monitoring** | UptimeRobot | Free |

---

## 📊 Key Insights Delivered

- **Daily price tracking** across 8 products and 100+ sellers
- **Best deal finder** — cheapest seller per category updated daily
- **Price change alerts** — biggest price jumps/drops vs yesterday and last week
- **Seller intelligence** — top rated sellers, trust scorecard, competition analysis
- **Historical trends** — average price over time with category grouping
- **Last updated indicator** — shows when the pipeline last ran with freshness status

---

## 👤 Author

**Dario Dang** — Data Analyst

[![GitHub](https://img.shields.io/badge/GitHub-DarioDang-black)](https://github.com/DarioDang)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-dario--dang-blue)](https://www.linkedin.com/in/dario-dang-89049020a/)
[![Portfolio](https://img.shields.io/badge/Portfolio-dariodang.github.io-orange)](https://dariodang.github.io)

---

*Built as part of the Data Engineering Zoomcamp 2026 cohort*