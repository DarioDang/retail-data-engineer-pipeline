# ml/config.py
# Single source of truth for all ML modeling decisions.
# Edit this file when adding/removing series or changing hyperparameters.
# Do NOT hardcode these values in train.py or predict.py.

# Seller exclusions
# Cross - border import resellers - fundamentally 
IMPORT_RESELLERS = [
    'Desertcart.ae',
    'desertcart.co.za',
    'desertcart.com.sa',
    'Ubuy',
    'u-buy.co.nz',
]

# Series excluded after training evaluation
# Format: (product_name, seller) tuples
EXCLUDED_SERIES = [
    # Generic eBay — multi-listing collapse (see 03_prophet_training.ipynb)
    ('Samsung Galaxy S24', 'eBay'),
    ('HP Spectre x360',    'eBay'),
    ('Samsung Galaxy A54', 'eBay'),
    ('Dell XPS 13',        'eBay'),
    # Regime shift in test period
    ('iPhone 15',          'Mobile City'),
    # High inherent volatility
    ('HP Spectre x360',    'eBay - samuraiheike'),
    ('Dell XPS 13',        'Microless.com'),
    ('MacBook Air M3',     'Auckland Airport'),
    # Insufficient data
    ('Samsung Galaxy A54', 'TechCrazy'),   # flat price — not a real forecast
    ('Samsung Galaxy S24', 'Kogan.com NZ'), # only 20 training rows
]

# Tier 1 threshold 
MIN_OBSERVATIONS = 31 # minimum days of history for a series to be modeled

# Prophet hyperparameters
DEFAULT_CHANGEPOINT_PRIOR_SCALE = 0.05

# Per-series overrides — only where tuning improved MAPE by >1%
# Format: {(product_name, seller): changepoint_prior_scale}
CHANGEPOINT_OVERRIDES = {
    ('Dell XPS 13',    'eBay - grassroots-computers'): 0.1,
    ('GoPro Hero 13',  'JB Hi-Fi'):                    0.3,
    ('MacBook Air M3', 'MightyApe.co.nz'):             0.1,
    ('HP Spectre x360','eBay - entique_australia'):     0.1,
}

# Prophet model settings (same for all series unless overriden above)
PROPHET_SETTINGS = {
    'yearly_seasonality':  False,  # only 60 days — can't learn yearly patterns
    'weekly_seasonality':  True,   # 8+ weekly cycles — learnable
    'daily_seasonality':   False,  # daily data, not sub-daily
}

# Forecast settings 
FORECAST_HORIZON_DAYS = 14   # how many days forward to forecast
HOLDOUT_DAYS         = 14   # days held out during training evaluation

# ── Production tiers ───────────────────────────────────────────────────────
# Used by the dashboard to show confidence level
TIER_A_MAPE_THRESHOLD = 5.0   # <5%  → high confidence
TIER_B_MAPE_THRESHOLD = 15.0  # <15% → acceptable

# ── Paths ──────────────────────────────────────────────────────────────────
from pathlib import Path
ML_DIR     = Path(__file__).parent
MODELS_DIR = ML_DIR / 'models'
MODELS_DIR.mkdir(exist_ok=True)

# ── Database ───────────────────────────────────────────────────────────────
MART_ML_SCHEMA       = 'dev_marts'
MART_ML_TABLE        = 'mart_ml'
FORECASTS_SCHEMA     = 'dev_marts'
FORECASTS_TABLE      = 'mart_forecasts'

# ── Regressor columns ──────────────────────────────────────────────────────
EXTRA_REGRESSORS = ['is_on_sale']

# ── S3 Model Storage ───────────────────────────────────────────────────────
S3_BUCKET      = 'dario-retail-price-pipeline'
S3_MODEL_PREFIX = 'ml/models/'   # s3://dario-retail-price-pipeline/ml/models/

# Local cache — models downloaded from S3 are cached here for faster
# subsequent runs. Gitignored — never committed to the repo.
# On Prefect managed workers this is ephemeral (wiped between runs),
# so predict.py always re-downloads fresh models from S3 in production.
MODELS_DIR.mkdir(exist_ok=True)