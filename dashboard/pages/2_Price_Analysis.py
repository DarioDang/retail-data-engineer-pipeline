import streamlit as st 
import streamlit.components.v1 as components
import plotly.express as px 
import pandas as pd 
import plotly.graph_objects as go 
from utils.styles import hide_streamlit_ui
import sys 
import os
import random
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.db import run_query
from utils.queries import (
    AVG_PRICE_OVER_TIME, PRICE_STATS_PER_PRODUCT,
    PRICE_RANGE_BY_PRODUCT, PRICE_CHANGE_VS_YESTERDAY,
    PRICE_CHANGE_VS_LAST_WEEK, PRICE_STATS_LAST_7_DAYS
)
from utils.sidebar import render_sidebar, BG_BASE64

st.set_page_config(layout="wide")

# Same global CSS — copy paste this block to every page
st.markdown(f"""
    <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpeg;base64,{BG_BASE64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        [data-testid="stAppViewContainer"]::before {{
            content: '';
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(14, 17, 23, 0.85);
            backdrop-filter: blur(2px);
            -webkit-backdrop-filter: blur(2px);
            z-index: 0;
            pointer-events: none;
        }}
        [data-testid="stAppViewContainer"] > * {{
            position: relative;
            z-index: 1;
        }}
        [data-testid="stHeader"] {{
            background: rgba(14, 17, 23, 0.8);
            backdrop-filter: blur(10px);
        }}
        h1 {{ text-align: center; }}
        h2 {{ text-align: center; }}
        h3 {{ text-align: center; }}
    </style>
""", unsafe_allow_html=True)


# Add sidebar
render_sidebar()

# Hide streamlit background
hide_streamlit_ui()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
        @keyframes gradientFlow {
            0%   { background-position: 0% 50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes iconPulse {
            0%,100% { transform: scale(1); filter: drop-shadow(0 0 0px rgba(255,107,107,0)); }
            50%      { transform: scale(1.08); filter: drop-shadow(0 0 8px rgba(255,107,107,0.6)); }
        }
        .page-title-text {
            background: linear-gradient(
                270deg,
                #FF6B6B,
                #f7971e,
                #fddb92,
                #38ef7d,
                #667eea,
                #f953c6,
                #FF6B6B
            );
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientFlow 4s ease infinite;
            font-size: 36px;
            font-weight: 800;
            letter-spacing: 3px;
            margin: 0;
        }
        .page-title-icon {
            animation: iconPulse 3s ease-in-out infinite;
        }
    </style>

    <div style="display:flex; align-items:center; justify-content:center; gap:14px; padding: 8px 0;">
        <img src="app/static/price-analysis.png" width="42" class="page-title-icon"/>
        <h1 class="page-title-text">PRICE ANALYSIS</h1>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        h1 { text-align: center; }
        h2 { text-align: center; }
        h3 { text-align: center; }
        .deal-card {
            background: linear-gradient(135deg, #1E2130 0%, #252840 100%);
            border-radius: 10px;
            padding: 14px 12px;
            margin: 4px 0;
            border-left: 3px solid #38ef7d;
            transition: transform 0.3s ease;
            text-align: center;
        }
        .deal-card:hover { transform: translateY(-4px); }
        .deal-rank { 
            color: #38ef7d; font-size: 11px; 
            font-weight: 700; letter-spacing: 1px; margin: 0;
        }
        .deal-product { 
            color: white; font-size: 13px; 
            font-weight: 700; margin: 4px 0; 
        }
        .deal-seller { color: gray; font-size: 11px; margin: 0; }
        .deal-price { 
            color: #38ef7d; font-size: 16px; 
            font-weight: 800; margin: 4px 0; 
        }
        .deal-savings { 
            color: #FF6B6B; font-size: 11px; 
            font-weight: 600; margin: 0;
        }
        .insight-card {
            background: #1E2130; border-radius: 12px; padding: 16px;
            margin: 6px 0; border-left: 4px solid #FF6B6B;
            transition: transform 0.3s ease;
        }
        .insight-card:hover { transform: translateX(6px); }
        .insight-title { color: gray; font-size: 12px; letter-spacing: 1px; margin: 0; }
        .insight-value { color: white; font-size: 22px; font-weight: 700; margin: 4px 0; }
        .insight-sub { color: gray; font-size: 12px; margin: 0; }
        div[data-testid="stButton"] button {
            border-radius: 25px;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            border: 2px solid #444;
            background: #1E2130;
            color: white;
        }
        div[data-testid="stButton"] button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255,107,107,0.3);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <p style='text-align: center; color: gray; font-size: 14px;'>
        Price trends and ranges across products
    </p>
""", unsafe_allow_html=True)
st.divider()

# ── STEP 1: Constants ──────────────────────────────────────────────────────────
CATEGORY_COLORS = {
    "laptop": "#667eea",
    "phone":  "#11998e",
    "camera": "#f7971e"
}

PRODUCT_ICONS = {
    "Dell XPS 13":        "app/static/dellxps-icon.png",
    "MacBook Air M3":     "app/static/macbookM3-icon.png",
    "HP Spectre x360":    "app/static/hpx360-icon.png",
    "iPhone 15":          "app/static/iphone15-icon.png",
    "Samsung Galaxy S24": "app/static/samsungs24-icon.png",
    "Samsung Galaxy A54": "app/static/samsungA54-icon.png",
    "GoPro Hero 13":      "app/static/gopro-icon.png",
    "DJI Osmo Action":    "app/static/dji-icon.png",
}

color_map = {
    "All":    "#FF6B6B",
    "laptop": "#667eea",
    "phone":  "#11998e",
    "camera": "#f7971e"
}

# ── STEP 2: Query all data ─────────────────────────────────────────────────────
df_stats = run_query(PRICE_STATS_PER_PRODUCT)
df_stats = df_stats.rename(columns={
    "product_name":   "Product",
    "category":       "Category",
    "seller_count":   "Seller Count",
    "min_price":      "Min Price (NZD)",
    "max_price":      "Max Price (NZD)",
    "avg_price":      "Avg Price (NZD)",
    "cheapest_seller":"Cheapest Seller",
    "cheapest_price": "Cheapest Price (NZD)",
    "savings_pct":    "Savings %",
    "avg_rating":     "Avg Rating",
    "avg_reviews":    "Avg Reviews",
})

df_trend = run_query(AVG_PRICE_OVER_TIME)

# ── STEP 3: Cheapest Seller + GLOBAL Filter ────────────────────────────────────
cheapest_df = df_stats[[
    "Product", "Category", "Cheapest Seller",
    "Cheapest Price (NZD)", "Avg Price (NZD)"
]].copy()
cheapest_df["Savings vs Avg (NZD)"] = (
    cheapest_df["Avg Price (NZD)"] - cheapest_df["Cheapest Price (NZD)"]
).round(2)
cheapest_df["Savings %"] = (
    (cheapest_df["Savings vs Avg (NZD)"] / cheapest_df["Avg Price (NZD)"]) * 100
).round(1)

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All"

# ── Animations + Card CSS ──────────────────────────────────────────────────────
st.markdown("""
    <style>
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(16px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulseGreen {
            0%   { box-shadow: 0 0 0 0 rgba(56, 239, 125, 0.4); }
            70%  { box-shadow: 0 0 0 8px rgba(56, 239, 125, 0); }
            100% { box-shadow: 0 0 0 0 rgba(56, 239, 125, 0); }
        }
        @keyframes shimmer {
            0%   { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        .best-deal-card {
            background: linear-gradient(135deg, #1a1d2e 0%, #1E2130 50%, #252840 100%);
            border-radius: 10px;
            padding: 12px 14px;
            margin: 4px 0;
            border-left: 3px solid #38ef7d;
            border-bottom: 1px solid rgba(56, 239, 125, 0.15);
            text-align: center;
            animation: fadeInUp 0.5s ease forwards;
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            position: relative;
            overflow: hidden;
        }
        .best-deal-card::before {
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 60%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(56, 239, 125, 0.04),
                transparent
            );
            animation: shimmer 3s infinite;
        }
        .best-deal-card:hover {
            transform: translateY(-5px) scale(1.01);
            box-shadow: 0 8px 24px rgba(56, 239, 125, 0.15);
            border-left-color: #38ef7d;
            animation: pulseGreen 1.5s ease;
        }
        .card-rank {
            color: #38ef7d;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1.5px;
            margin: 0 0 4px 0;
            text-transform: uppercase;
        }
        .card-product {
            color: white;
            font-size: 13px;
            font-weight: 700;
            margin: 3px 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .card-seller {
            color: #8892a4;
            font-size: 10px;
            margin: 2px 0;
            font-style: italic;
        }
        .card-price {
            background: linear-gradient(90deg, #38ef7d, #11998e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 15px;
            font-weight: 800;
            margin: 4px 0 2px 0;
            letter-spacing: 0.5px;
        }
        .card-savings {
            color: #FF6B6B;
            font-size: 10px;
            font-weight: 700;
            margin: 0;
            letter-spacing: 0.5px;
        }
        .card-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(56,239,125,0.3), transparent);
            margin: 6px 0;
        }
    </style>
""", unsafe_allow_html=True)

filter_col, cards_col = st.columns([1, 4])

with filter_col:
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

            div[data-testid="stButton"] {
                margin: 0 !important;
                padding: 0 !important;
                position: relative;
                top: -50px;
                margin-bottom: -50px !important;
                height: 42px !important;
            }

            div[data-testid="stButton"] > button {
                width: 100% !important;
                height: 42px !important;
                min-height: 42px !important;
                max-height: 42px !important;
                background: transparent !important;
                border: none !important;
                color: transparent !important;
                font-size: 0 !important;
                padding: 0 !important;
                margin: 0 !important;
                cursor: pointer !important;
                box-shadow: none !important;
                outline: none !important;
            }

            div[data-testid="stButton"] > button:hover,
            div[data-testid="stButton"] > button:focus {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
            }

            .filter-item {
                height: 42px;
                width: 100%;
                margin-bottom: 8px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 1.5px;
                font-family: 'Space Grotesk', sans-serif;
                text-transform: uppercase;
                box-sizing: border-box;
                transition: all 0.2s ease;
            }

            .filter-inactive {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.07);
                color: rgba(255,255,255,0.35);
            }
        </style>
    """, unsafe_allow_html=True)

    selected_category = st.session_state.selected_category

    categories = [
        ("cat_all",    "all-icon.png",    "ALL",    "All",    "#a78bfa", "26,0,96"),
        ("cat_laptop", "laptop-icon.png", "LAPTOP", "laptop", "#38ef7d", "0,61,28"),
        ("cat_phone",  "mobile-icon.png",  "PHONE",  "phone",  "#60a5fa", "0,32,90"),
        ("cat_camera", "camera-icon.png", "CAMERA", "camera", "#fb923c", "74,21,0"),
    ]

    for key, icon, label, cat_value, cat_color, text_dark in categories:
        is_active = (selected_category == cat_value)
        r, g, b = tuple(int(cat_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

        # Adjust the all icon to the left 
        icon_margin = "-20px" if icon == "all-icon.png" else "0px"

        if is_active:
            item_style = f"""
                background: {cat_color};
                color: rgb({text_dark});
                box-shadow: 0 4px 16px rgba({r},{g},{b},0.45);
            """
            item_class = ""
        else:
            item_style = ""
            item_class = "filter-inactive"

        st.markdown(f"""
            <div class='filter-item {item_class}' style='{item_style}'>
                <img src='app/static/{icon}'
                    style='width:20px; height:20px; object-fit:contain; 
                            margin-right:8px; margin-left:{icon_margin};'/>
                {label}
            </div>
        """, unsafe_allow_html=True)

        if st.button("​", use_container_width=True, key=key):
            st.session_state.selected_category = cat_value
            st.rerun()

    # Active indicator bar
    selected_category = st.session_state.selected_category
    active_color = color_map[selected_category]
    r, g, b = tuple(int(active_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

CATEGORY_ICONS = {
    "laptop": "laptop-icon.png",
    "phone":  "mobile-icon.png",
    "camera": "camera-icon.png",
}

with cards_col:
    filtered_deals = cheapest_df.copy()

    if selected_category != "All":
        filtered_deals = filtered_deals[
            filtered_deals["Category"] == selected_category
        ]
        top3 = filtered_deals.nlargest(3, "Savings %")
        rank_labels = ["BEST DEAL", "2ND DEAL", "3RD DEAL"]

        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

        # ── Dynamic columns based on actual number of products ─────────────────
        num_products = len(top3)
        if num_products == 3:
            _, c1, c2, c3, _ = st.columns([0.5, 2, 2, 2, 0.5])
            all_cols = [c1, c2, c3]
        elif num_products == 2:
            _, c1, c2, _ = st.columns([1, 2, 2, 1])
            all_cols = [c1, c2]
        else:
            _, c1, _ = st.columns([2, 2, 2])
            all_cols = [c1]

        top4 = top3
    else:
        best_laptop = filtered_deals[filtered_deals["Category"] == "laptop"].nlargest(1, "Savings %")
        best_phone  = filtered_deals[filtered_deals["Category"] == "phone"].nlargest(1, "Savings %")
        best_camera = filtered_deals[filtered_deals["Category"] == "camera"].nlargest(1, "Savings %")

        top4 = pd.concat([best_laptop, best_phone, best_camera]).drop_duplicates(subset=["Product"])
        rank_labels = ["LAPTOP", "PHONE", "CAMERA"]

        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

        _, c1, c2, c3, _ = st.columns([0.5, 2, 2, 2, 0.5])
        all_cols = [c1, c2, c3]

    if len(top4) == 0:
        st.info("No data available for selected category.")
    else:
        for i, (col, (_, row)) in enumerate(zip(all_cols, top4.iterrows())):
            delay     = i * 0.15
            category  = row["Category"]
            cat_color = CATEGORY_COLORS.get(category, "#38ef7d")
            cat_icon  = CATEGORY_ICONS.get(category, "all-icon.png")
            r, g, b   = tuple(int(cat_color.lstrip("#")[j:j+2], 16) for j in (0, 2, 4))
            card_id   = f"spark_{i}_{category}"

            # ── Real price trend for this product ──
            product_name = row["Product"]
            trend = df_trend[df_trend["product_name"] == product_name].sort_values("snapshot_date")
            
            if len(trend) >= 2:
                points = trend["avg_price"].tolist()
            else:
                # fallback to random if not enough data
                points = [random.randint(20, 80) for _ in range(10)]

            min_p, max_p = min(points), max(points)
            w, h = 200, 40
            coords = []
            for idx, p in enumerate(points):
                x = int(idx * w / (len(points) - 1))
                y = h - int((p - min_p) / max(max_p - min_p, 1) * (h - 8)) - 4
                coords.append(f"{x},{y}")
            polyline  = " ".join(coords)
            fill_poly = polyline + f" {w},{h} 0,{h}"

            with col:
                st.markdown(f"""
                    <style>
                        @keyframes dash_{card_id} {{
                            from {{ stroke-dashoffset: 400; }}
                            to   {{ stroke-dashoffset: 0; }}
                        }}
                        @keyframes fadeFill_{card_id} {{
                            from {{ opacity: 0; }}
                            to   {{ opacity: 1; }}
                        }}
                        @keyframes moveSpark_{card_id} {{
                            0%   {{ transform: translateX(0px);  }}
                            50%  {{ transform: translateX(-6px); }}
                            100% {{ transform: translateX(0px);  }}
                        }}
                        .spark-wrap_{card_id} {{
                            animation: moveSpark_{card_id} 4s ease-in-out infinite;
                        }}
                    </style>
                    <div class='best-deal-card'
                         style='animation-delay: {delay}s; border-left-color: {cat_color};
                                transition: transform 0.25s ease, box-shadow 0.25s ease;'
                         onmouseover="this.style.transform='translateY(-6px)';
                                      this.style.boxShadow='0 12px 28px rgba({r},{g},{b},0.3)';"
                         onmouseout="this.style.transform='translateY(0px)';
                                     this.style.boxShadow='';">
                        <p class='card-rank' style='color: {cat_color};'>
                            <img src='app/static/{cat_icon}'
                                 style='width:20px; height:20px; object-fit:contain;
                                        vertical-align:middle; margin-right:8px;'/>
                            {rank_labels[i]}
                        </p>
                        <p class='card-product'>{row['Product']}</p>
                        <p class='card-seller'>via {row['Cheapest Seller']}</p>
                        <div class='card-divider'
                             style='background: linear-gradient(90deg, transparent,
                             rgba({r},{g},{b}, 0.3), transparent);'></div>
                        <div class='spark-wrap_{card_id}'
                             style='margin: 6px 0; overflow: hidden; border-radius: 4px;'>
                            <svg viewBox='0 0 {w} {h}' width='100%' height='{h}'
                                 xmlns='http://www.w3.org/2000/svg'>
                                <defs>
                                    <linearGradient id='grad_{card_id}' x1='0' y1='0' x2='0' y2='1'>
                                        <stop offset='0%' stop-color='rgba({r},{g},{b},0.25)'/>
                                        <stop offset='100%' stop-color='rgba({r},{g},{b},0)'/>
                                    </linearGradient>
                                </defs>
                                <polygon
                                    points='{fill_poly}'
                                    fill='url(#grad_{card_id})'
                                    style='animation: fadeFill_{card_id} 1.2s ease {delay}s both;'/>
                                <polyline
                                    points='{polyline}'
                                    fill='none'
                                    stroke='rgba({r},{g},{b},0.9)'
                                    stroke-width='1.8'
                                    stroke-linecap='round'
                                    stroke-linejoin='round'
                                    stroke-dasharray='400'
                                    stroke-dashoffset='400'
                                    style='animation: dash_{card_id} 1.2s ease {delay}s forwards;'/>
                                <circle
                                    cx='{coords[-1].split(",")[0]}'
                                    cy='{coords[-1].split(",")[1]}'
                                    r='3'
                                    fill='{cat_color}'/>
                            </svg>
                        </div>
                        <p class='card-price'>NZD {row['Cheapest Price (NZD)']:,.2f}</p>
                        <p class='card-savings'>⬇ Save {row['Savings %']}%</p>
                    </div>
                """, unsafe_allow_html=True)

selected_category = st.session_state.selected_category
st.divider()

# ── STEP 4: Apply global filter to all data ────────────────────────────────────
df_range = run_query(PRICE_RANGE_BY_PRODUCT)
if selected_category != "All":
    df_range = df_range[df_range["category"] == selected_category]

df_stats_filtered = df_stats.copy()
if selected_category != "All":
    df_stats_filtered = df_stats_filtered[
        df_stats_filtered["Category"] == selected_category
    ]

# ── STEP 5: Average Price Over Time ───────────────────────────────────────────
# ── STEP 5: Average Price Over Time ───────────────────────────────────────────
df_time = run_query(AVG_PRICE_OVER_TIME)
df_time["snapshot_date"] = pd.to_datetime(df_time["snapshot_date"]).dt.date

if selected_category != "All":
    df_time = df_time[df_time["category"] == selected_category]

if len(df_time["snapshot_date"].unique()) > 1:
    products   = sorted(df_time["product_name"].unique().tolist())
    all_dates  = sorted(df_time["snapshot_date"].unique())
    total_days = len(all_dates)

    default_start     = all_dates[-min(7, total_days)]
    default_end       = all_dates[-1]
    date_options      = {d.strftime("%d %b %Y"): d for d in all_dates}
    date_labels       = list(date_options.keys())
    default_start_idx = max(0, len(all_dates) - 7)
    default_end_idx   = len(all_dates) - 1

    # ── Title row + inline filter ──────────────────────────────────────────────
    st.markdown("""
        <style>
            div[data-testid="stSelectbox"] {
                background: rgba(255,255,255,0.03) !important;
                border-radius: 8px !important;
                border: 1px solid rgba(255,107,107,0.2) !important;
                padding: 0 !important;
            }
            div[data-testid="stSelectbox"]:hover {
                border-color: rgba(255,107,107,0.5) !important;
            }
            div[data-testid="stSelectbox"] label p {
                color: rgba(255,255,255,0.35) !important;
                font-size: 9px !important;
                font-weight: 700 !important;
                letter-spacing: 2px !important;
                text-transform: uppercase !important;
                margin-bottom: 0 !important;
            }
            div[data-testid="stSelectbox"] [data-baseweb="select"] div {
                background: transparent !important;
                color: #FF6B6B !important;
                font-weight: 600 !important;
                font-size: 11px !important;
                border: none !important;
                box-shadow: none !important;
                min-height: 26px !important;
                padding: 0 4px !important;
            }
            div[data-testid="stSelectbox"] svg {
                fill: #FF6B6B !important;
                width: 12px !important;
                height: 12px !important;
            }
            [data-baseweb="popover"] ul {
                background: #1a1d2e !important;
                border: 1px solid rgba(255,107,107,0.2) !important;
                border-radius: 10px !important;
                padding: 4px !important;
            }
            [data-baseweb="popover"] li {
                color: rgba(255,255,255,0.7) !important;
                font-size: 11px !important;
                background: transparent !important;
                border-radius: 6px !important;
                padding: 6px 10px !important;
            }
            [data-baseweb="popover"] li:hover {
                background: rgba(255,107,107,0.15) !important;
                color: #FF6B6B !important;
            }
        </style>
    """, unsafe_allow_html=True)

    title_col, _, from_col, to_col = st.columns([4, 0.5, 1.2, 1.2])

    with title_col:
        st.subheader("AVERAGE PRICE OVER TIME")

    with from_col:
        start_label = st.selectbox(
            "FROM", options=date_labels,
            index=default_start_idx, key="date_start"
        )

    with to_col:
        end_label = st.selectbox(
            "TO", options=date_labels,
            index=default_end_idx, key="date_end"
        )

    selected_start = date_options[start_label]
    selected_end   = date_options[end_label]

    # ── Filter by date ─────────────────────────────────────────────────────────
    df_time_filtered = df_time[
        (df_time["snapshot_date"] >= selected_start) &
        (df_time["snapshot_date"] <= selected_end)
    ]

    # ── Group products by category ─────────────────────────────────────────────
    category_order  = ["laptop", "phone", "camera"]
    category_labels = {
        "laptop": "LAPTOP",
        "phone":  "PHONE",
        "camera": "CAMERA"
    }
    category_icons = {
        "laptop": "laptop-cat-icon.png",
        "phone":  "mobile-cat-icon.png",
        "camera": "camera-cat-icon.png"
    }

    def render_product_chart(product, df_time_filtered):
        df_product = df_time_filtered[
            df_time_filtered["product_name"] == product
        ].copy()

        if df_product.empty:
            return False

        df_product["snapshot_date"] = df_product["snapshot_date"].astype(str)
        category   = df_product["category"].iloc[0]
        line_color = CATEGORY_COLORS.get(category, "#FF6B6B")
        icon_path  = PRODUCT_ICONS.get(product, "")

        if len(df_product) >= 2:
            first_price  = df_product["avg_price"].iloc[0]
            last_price   = df_product["avg_price"].iloc[-1]
            change_pct   = ((last_price - first_price) / first_price) * 100
            change_color = "#2ECC71" if change_pct <= 0 else "#FF6B6B"
            change_arrow = "▼" if change_pct <= 0 else "▲"
            change_text  = f"{change_arrow} {abs(change_pct):.1f}%"
        else:
            change_text  = "–"
            change_color = "gray"

        y_min     = df_product["avg_price"].min()
        y_max     = df_product["avg_price"].max()
        y_padding = (y_max - y_min) * 0.15 if y_max != y_min else y_max * 0.05
        y_range   = [y_min - y_padding, y_max + y_padding]

        fig = px.line(
            df_product, x="snapshot_date", y="avg_price",
            markers=True, title="",
            labels={"snapshot_date": "Date", "avg_price": "Avg Price (NZD)"}
        )
        fig.update_layout(
            xaxis=dict(
                type="category", tickangle=-45, tickmode="array",
                tickvals=df_product["snapshot_date"].tolist(),
                tickfont=dict(size=10, color="rgba(255,255,255,0.5)"),
                gridcolor="rgba(255,255,255,0.03)",
                range=[-0.5, len(df_product) - 0.5],
            ),
            yaxis=dict(
                range=y_range, tickprefix="$",
                tickfont=dict(size=10, color="rgba(255,255,255,0.5)"),
                gridcolor="rgba(255,255,255,0.05)",
            ),
            showlegend=False, height=300,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=10, r=10),
        )
        r, g, b = int(line_color[1:3], 16), int(line_color[3:5], 16), int(line_color[5:7], 16)
        fig.update_traces(
            line_color=line_color, line_width=2.5,
            marker=dict(size=8, color=line_color, line=dict(width=2, color="white")),
            fill="tozeroy",
            fillcolor=f"rgba({r},{g},{b},0.08)",
        )
        custom_title = f"""
            <div style='text-align:center; margin-top:16px; margin-bottom:4px;
                padding:8px 12px; display:flex; align-items:center;
                justify-content:center; gap:8px;'>
                <img src='{icon_path}' width='24' style='vertical-align:middle;'/>
                <span style='color:white; font-size:14px; font-weight:600;'>{product}</span>
                <span style='color:{change_color}; font-size:12px; font-weight:700;
                    background:rgba(0,0,0,0.3); padding:2px 8px;
                    border-radius:8px;'>{change_text}</span>
            </div>
        """
        st.markdown(custom_title, unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        return True

    # ── Render by category groups ──────────────────────────────────────────────
    categories_to_show = (
        [selected_category] if selected_category != "All"
        else category_order
    )

    for cat in categories_to_show:
        cat_products = [
            p for p in products
            if not df_time_filtered[df_time_filtered["product_name"] == p].empty
            and df_time_filtered[
                df_time_filtered["product_name"] == p
            ]["category"].values[0] == cat
        ]

        if not cat_products:
            continue

        cat_color = CATEGORY_COLORS.get(cat, "#FF6B6B")
        cat_icon  = category_icons.get(cat, "all-icon.png")
        cat_label = category_labels.get(cat, cat.upper())

        st.markdown(f"""
            <div style='
                display:flex; align-items:center; justify-content:center;
                gap:10px; margin:24px 0 8px 0; padding:8px 16px;
                background:rgba(255,255,255,0.03); border-radius:8px;
                border-left:3px solid {cat_color};
                border-right:3px solid {cat_color};
            '>
                <div style='flex:1; height:1px;
                    background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08));'>
                </div>
                <img src='app/static/{cat_icon}' width='18' height='18'
                    style='vertical-align:middle;'/>
                <span style='color:{cat_color}; font-size:11px; font-weight:800;
                    letter-spacing:3px; text-transform:uppercase;'>
                    {cat_label} CATEGORY
                </span>
                <div style='flex:1; height:1px;
                    background:linear-gradient(90deg,rgba(255,255,255,0.08),transparent);'>
                </div>
            </div>
        """, unsafe_allow_html=True)

        for row_start in range(0, len(cat_products), 3):
            row_products = cat_products[row_start:row_start + 3]
            cols = st.columns(len(row_products))
            for col, product in zip(cols, row_products):
                with col:
                    render_product_chart(product, df_time_filtered)

else:
    st.info("⏳ Time series will populate after multiple daily pipeline runs.")
    fig = px.bar(
        df_time, x="product_name", y="avg_price", color="category",
        color_discrete_map=CATEGORY_COLORS,
        labels={"product_name": "Product", "avg_price": "Average Price (NZD)"}
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── STEP 6: Price Range Box Plot ───────────────────────────────────────────────
st.subheader("PRICE RANGE BY PRODUCT")
fig = px.box(
    df_range, x="product_name", y="price", color="category",
    color_discrete_map=CATEGORY_COLORS,
    labels={"product_name": "Product", "price": "Price (NZD)"}
)
fig.update_layout(
    xaxis_tickangle=-45,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(fig, use_container_width=True)
st.divider()

# ── STEP 7: Price Statistics Insight Cards ─────────────────────────────────────
st.subheader("PRICE STATISTICS PER PRODUCT")

# ── Fetch time-aware data ──────────────────────────────────────────────────────
df_yesterday = run_query(PRICE_CHANGE_VS_YESTERDAY)
df_week      = run_query(PRICE_CHANGE_VS_LAST_WEEK)

# ── Apply category filter ──────────────────────────────────────────────────────
if selected_category != "All":
    df_yesterday = df_yesterday[df_yesterday["category"] == selected_category]
    df_week      = df_week[df_week["category"] == selected_category]

# ── Fallback to df_stats_filtered if not enough time data ─────────────────────
has_yesterday = len(df_yesterday) > 0
has_week      = len(df_week) > 0

# ── PAGE 1: Today's snapshot insights 
# ── Fetch last 7 days stats 
df_7days = run_query(PRICE_STATS_LAST_7_DAYS)

if selected_category != "All":
    df_7days = df_7days[df_7days["category"] == selected_category]

# ── Use 7-day data if available, fallback to all-time 
if len(df_7days) > 0:
    most_expensive_row  = df_7days.loc[df_7days["max_price_7d"].idxmax()]
    cheapest_avg_row    = df_7days.loc[df_7days["avg_price_7d"].idxmin()]

    most_expensive_val  = f"NZD {most_expensive_row['max_price_7d']:,.2f}"
    most_expensive_sub  = f"{most_expensive_row['product_name']} (7d)"
    cheapest_avg_val    = f"NZD {cheapest_avg_row['avg_price_7d']:,.2f}"
    cheapest_avg_sub    = f"{cheapest_avg_row['product_name']} (7d)"
else:
    most_expensive      = df_stats_filtered.loc[df_stats_filtered["Max Price (NZD)"].idxmax()]
    cheapest_avg        = df_stats_filtered.loc[df_stats_filtered["Avg Price (NZD)"].idxmin()]
    most_expensive_val  = f"NZD {most_expensive['Max Price (NZD)']:,.2f}"
    most_expensive_sub  = most_expensive["Product"]
    cheapest_avg_val    = f"NZD {cheapest_avg['Avg Price (NZD)']:,.2f}"
    cheapest_avg_sub    = cheapest_avg["Product"]

most_sellers = df_stats_filtered.loc[df_stats_filtered["Seller Count"].idxmax()]
best_deal    = df_stats_filtered.loc[df_stats_filtered["Cheapest Price (NZD)"].idxmin()]

# ── PAGE 2: Time-aware insights ────────────────────────────────────────────────
if has_yesterday:
    # Biggest price jump vs yesterday
    biggest_jump = df_yesterday.loc[df_yesterday["pct_change"].idxmax()]
    jump_val     = f"▲ {biggest_jump['pct_change']:.1f}%"
    jump_sub     = biggest_jump["product_name"]
    jump_color   = "#FF6B6B"

    # Biggest price drop vs yesterday
    biggest_drop = df_yesterday.loc[df_yesterday["pct_change"].idxmin()]
    drop_val     = f"▼ {abs(biggest_drop['pct_change']):.1f}%"
    drop_sub     = biggest_drop["product_name"]
    drop_color   = "#38ef7d"
else:
    jump_val   = "N/A"
    jump_sub   = "Need 2+ days of data"
    jump_color = "#FF6B6B"
    drop_val   = "N/A"
    drop_sub   = "Need 2+ days of data"
    drop_color = "#38ef7d"

if has_week:
    # Biggest weekly price drop (best time to buy)
    best_weekly  = df_week.loc[df_week["pct_change_week"].idxmin()]
    weekly_val   = f"▼ {abs(best_weekly['pct_change_week']):.1f}%"
    weekly_sub   = f"{best_weekly['product_name']} vs last week"
    weekly_color = "#00c9ff"

    # Biggest weekly price jump (price alert)
    alert_weekly  = df_week.loc[df_week["pct_change_week"].idxmax()]
    alert_val     = f"▲ {alert_weekly['pct_change_week']:.1f}%"
    alert_sub     = f"{alert_weekly['product_name']} vs last week"
    alert_color   = "#f953c6"
else:
    weekly_val   = "N/A"
    weekly_sub   = "Need 7+ days of data"
    weekly_color = "#00c9ff"
    alert_val    = "N/A"
    alert_sub    = "Need 7+ days of data"
    alert_color  = "#f953c6"

# ── Ratings & reviews from stats ──────────────────────────────────────────────
has_reviews = "Avg Reviews" in df_stats_filtered.columns
has_rating  = "Avg Rating"  in df_stats_filtered.columns
has_min     = "Min Price (NZD)" in df_stats_filtered.columns
has_savings = "Savings %" in df_stats_filtered.columns

most_reviewed   = df_stats_filtered.loc[df_stats_filtered["Avg Reviews"].idxmax()] if has_reviews else most_sellers
highest_rated   = df_stats_filtered.loc[df_stats_filtered["Avg Rating"].idxmax()]  if has_rating  else cheapest_avg
price_range_row = df_stats_filtered.loc[(df_stats_filtered["Max Price (NZD)"] - df_stats_filtered["Min Price (NZD)"]).idxmax()] if has_min else most_expensive

reviews_val = f"{int(most_reviewed['Avg Reviews']):,}" if has_reviews else "N/A"
rating_val  = f"★ {highest_rated['Avg Rating']:.1f}"   if has_rating  else "N/A"
range_val   = f"NZD {(price_range_row['Max Price (NZD)'] - price_range_row['Min Price (NZD)']):,.2f}" if has_min else "N/A"
range_prod  = price_range_row["Product"] if has_min else most_expensive["Product"]

# ── Build pages ────────────────────────────────────────────────────────────────
def make_card(color, title, value, sub, pct):
    return f"""<div class="ic-wrap" style="--ic:{color};"
         onmouseover="this.style.boxShadow='0 12px 30px {color}33';this.style.transform='translateY(-5px)';"
         onmouseout="this.style.boxShadow='';this.style.transform='translateY(0)';">
        <div class="ic-bar"></div>
        <div class="ic-scan"></div>
        <div class="ic-dot-tl"></div>
        <div class="ic-dot-br"></div>
        <p class="ic-title">{title}</p>
        <p class="ic-value">{value}</p>
        <p class="ic-sub">{sub}</p>
        <div class="ic-progress-wrap">
            <div class="ic-progress-fill" style="--pct:{pct};"></div>
        </div>
    </div>"""

# Page 1 — Today's snapshot
page1 = (
    make_card("#FF6B6B", "MOST EXPENSIVE (7D)", most_expensive_val, most_expensive_sub, "85%") +
    make_card("#38ef7d", "LOWEST AVG (7D)",     cheapest_avg_val,   cheapest_avg_sub,   "40%") +
    make_card("#667eea", "MOST COMPETITIVE",    f"{int(most_sellers['Seller Count'])} sellers", most_sellers['Product'], "70%") +
    make_card("#f7971e", "BEST DEAL TODAY",     f"NZD {best_deal['Cheapest Price (NZD)']:,.2f}", best_deal['Cheapest Seller'], "60%")
)

# Page 2 — vs Yesterday
page2 = (
    make_card(jump_color,   "PRICE JUMP ↑ VS YESTERDAY",  jump_val,   jump_sub,                              "85%") +
    make_card(drop_color,   "PRICE DROP ↓ VS YESTERDAY",  drop_val,   drop_sub,                              "40%") +
    make_card(alert_color,  "PRICE ALERT ↑ THIS WEEK",    alert_val,  alert_sub,                             "75%") +
    make_card(weekly_color, "BEST DROP ↓ THIS WEEK",      weekly_val, weekly_sub,                            "55%")
)

# Page 3 — Historical stats
page3 = (
    make_card("#fddb92", "HIGHEST RATED",    rating_val,  highest_rated['Product'] if has_rating else "N/A",  "65%") +
    make_card("#00c9ff", "MOST REVIEWED",    reviews_val, most_reviewed['Product'] if has_reviews else "N/A", "55%") +
    make_card("#a8edea", "BIGGEST RANGE",    range_val,   range_prod,                                         "50%") +
    make_card("#f953c6", "MOST SELLERS",     f"{int(most_sellers['Seller Count'])} sellers", most_sellers['Product'], "70%")
)

html = f"""<!DOCTYPE html>
<html>
<head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700;800&display=swap');
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ background:transparent; font-family:'Space Grotesk',sans-serif; overflow:hidden; }}

    @keyframes floatDot {{
        0%,100% {{ transform:translateY(0); opacity:0.6; }}
        50%      {{ transform:translateY(-5px); opacity:1; }}
    }}
    @keyframes scanline {{
        0%   {{ top:0%; }}
        100% {{ top:100%; }}
    }}
    @keyframes countUp {{
        from {{ opacity:0; transform:scale(0.85); }}
        to   {{ opacity:1; transform:scale(1); }}
    }}
    @keyframes progressGrow {{
        from {{ width:0%; }}
        to   {{ width:var(--pct); }}
    }}
    @keyframes fadeSlideUp {{
        from {{ opacity:0; transform:translateY(20px); }}
        to   {{ opacity:1; transform:translateY(0); }}
    }}

    body {{ width:100%; }}

    .ic-outer {{
        width: 100%;
        overflow: hidden;
        position: relative;
        padding: 8px 0 4px 0;
    }}
    .ic-outer::before,
    .ic-outer::after {{
        content:'';
        position:absolute;
        top:0; bottom:0;
        width:20px;
        z-index:2;
        pointer-events:none;
    }}
    .ic-outer::before {{
        left:0;
        background:linear-gradient(to right,#0e1117,transparent);
    }}
    .ic-outer::after {{
        right:0;
        background:linear-gradient(to left,#0e1117,transparent);
    }}
    .ic-track {{
        display: flex;
        flex-wrap: nowrap;
        gap: 0;
        transition: transform 0.85s cubic-bezier(0.4,0,0.2,1);
        will-change: transform;
    }}
    .ic-page {{
        display: flex;
        flex-shrink: 0;
        gap: 12px;
        padding: 0 40px;
    }}
    .ic-wrap {{
        position: relative;
        border-radius: 14px;
        padding: 20px 16px 16px 16px;
        text-align: center;
        border: 1px solid var(--ic);
        background: linear-gradient(160deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
        overflow: hidden;
        animation: fadeSlideUp 0.6s ease both;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        cursor: default;
        flex: 1;
        height: 170px;
        min-height: 170px;
    }}
    .ic-bar {{
        position:absolute; top:0; left:0; right:0;
        height:3px; background:var(--ic);
        border-radius:14px 14px 0 0;
    }}
    .ic-scan {{
        position:absolute; left:0; right:0; height:40%;
        background:linear-gradient(to bottom,transparent,rgba(255,255,255,0.03),transparent);
        animation:scanline 3s linear infinite;
        pointer-events:none;
    }}
    .ic-dot-tl, .ic-dot-br {{
        position:absolute; width:5px; height:5px;
        border-radius:50%; background:var(--ic);
        animation:floatDot 2.5s ease-in-out infinite;
    }}
    .ic-dot-tl {{ top:10px; left:10px; animation-delay:0s; }}
    .ic-dot-br {{ bottom:10px; right:10px; animation-delay:1.2s; }}
    .ic-title {{
        color:var(--ic);
        font-size: 9px;
        font-weight: 800;
        letter-spacing: 2.5px;
        margin: 8px 0 10px 0;
        text-transform: uppercase;
        opacity: 0.85;
    }}
    .ic-value {{
        font-size: 20px;
        font-weight: 800;
        color: white;
        margin: 0 0 6px 0;
        letter-spacing: 0.5px;
        animation: countUp 0.7s ease both;
    }}
    .ic-sub {{
        color: rgba(255,255,255,0.45);
        font-size: 10px;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        letter-spacing: 0.5px;
    }}
    .ic-progress-wrap {{
        margin-top: 12px;
        height: 3px;
        border-radius: 99px;
        background: rgba(255,255,255,0.06);
        overflow: hidden;
    }}
    .ic-progress-fill {{
        height: 100%;
        border-radius: 99px;
        background: var(--ic);
        animation: progressGrow 1.2s ease both;
    }}
    .ic-indicators {{
        display:flex; justify-content:center;
        gap:6px; margin-top:12px;
    }}
    .ic-dot {{
        width:6px; height:6px; border-radius:50%;
        background:rgba(255,255,255,0.2);
        transition:all 0.4s ease; cursor:pointer;
    }}
    .ic-dot.active {{
        background:white; width:18px; border-radius:99px;
    }}
</style>
</head>
<body>
    <div class="ic-outer" id="icOuter">
        <div class="ic-track" id="icTrack">

            <!-- PAGE 1: Today's snapshot -->
            <div class="ic-page" id="p0">
                {make_card("#FF6B6B", "MOST EXPENSIVE (7D)", most_expensive_val, most_expensive_sub, "85%")}
                {make_card("#38ef7d", "LOWEST AVG (7D)",     cheapest_avg_val,   cheapest_avg_sub,   "40%")}
                {make_card("#667eea", "MOST COMPETITIVE",    f"{int(most_sellers['Seller Count'])} sellers", most_sellers['Product'], "70%")}
                {make_card("#f7971e", "BEST DEAL TODAY",     f"NZD {best_deal['Cheapest Price (NZD)']:,.2f}", best_deal['Cheapest Seller'], "60%")}
            </div>

            <!-- PAGE 2: vs Yesterday & This Week -->
            <div class="ic-page" id="p1">
                {make_card(jump_color,   "PRICE JUMP ↑ VS YESTERDAY", jump_val,   jump_sub,   "85%")}
                {make_card(drop_color,   "PRICE DROP ↓ VS YESTERDAY", drop_val,   drop_sub,   "40%")}
                {make_card(alert_color,  "PRICE ALERT ↑ THIS WEEK",   alert_val,  alert_sub,  "75%")}
                {make_card(weekly_color, "BEST DROP ↓ THIS WEEK",     weekly_val, weekly_sub, "55%")}
            </div>

            <!-- PAGE 3: Historical stats -->
            <div class="ic-page" id="p2">
                {make_card("#fddb92", "HIGHEST RATED",  rating_val,  highest_rated['Product'] if has_rating else "N/A",  "65%")}
                {make_card("#00c9ff", "MOST REVIEWED",  reviews_val, most_reviewed['Product'] if has_reviews else "N/A", "55%")}
                {make_card("#a8edea", "BIGGEST RANGE",  range_val,   range_prod,                                         "50%")}
                {make_card("#f953c6", "MOST SELLERS",   f"{int(most_sellers['Seller Count'])} sellers", most_sellers['Product'], "70%")}
            </div>

            <!-- PAGE 1 CLONE for seamless loop -->
            <div class="ic-page" id="p3">
                {make_card("#FF6B6B", "MOST EXPENSIVE (7D)", most_expensive_val, most_expensive_sub, "85%")}
                {make_card("#38ef7d", "LOWEST AVG (7D)",     cheapest_avg_val,   cheapest_avg_sub,   "40%")}
                {make_card("#667eea", "MOST COMPETITIVE",    f"{int(most_sellers['Seller Count'])} sellers", most_sellers['Product'], "70%")}
                {make_card("#f7971e", "BEST DEAL TODAY",     f"NZD {best_deal['Cheapest Price (NZD)']:,.2f}", best_deal['Cheapest Seller'], "60%")}
            </div>

        </div>
    </div>

    <div class="ic-indicators">
        <div class="ic-dot active" id="dot0"></div>
        <div class="ic-dot"        id="dot1"></div>
        <div class="ic-dot"        id="dot2"></div>
    </div>

    <script>
        const track  = document.getElementById('icTrack');
        const outer  = document.getElementById('icOuter');
        const dots   = [
            document.getElementById('dot0'),
            document.getElementById('dot1'),
            document.getElementById('dot2'),
        ];
        let   page   = 0;
        let   timer  = null;
        let   locked = false;
        const TOTAL  = 3;

        function init() {{
            const W = outer.offsetWidth;
            document.querySelectorAll('.ic-page').forEach(p => {{
                p.style.width    = W + 'px';
                p.style.minWidth = W + 'px';
            }});
        }}

        function setDots(p) {{
            dots.forEach((d, i) => d.classList.toggle('active', i === p));
        }}

        function slideTo(p, animate) {{
            const W = outer.offsetWidth;
            if (!animate) track.style.transition = 'none';
            track.style.transform = 'translateX(-' + (p * W) + 'px)';
            if (!animate) void track.offsetWidth;
            if (!animate) track.style.transition = '0.85s cubic-bezier(0.4,0,0.2,1)';
        }}

        function next() {{
            if (locked) return;
            locked = true;
            const nextPage = page + 1;
            if (nextPage < TOTAL) {{
                page = nextPage;
                setDots(page);
                slideTo(page, true);
                setTimeout(() => {{ locked = false; }}, 900);
            }} else {{
                // slide to clone then snap back to page 0
                slideTo(TOTAL, true);
                setDots(0);
                setTimeout(() => {{
                    slideTo(0, false);
                    page = 0;
                    locked = false;
                }}, 900);
            }}
        }}

        function startTimer() {{ timer = setInterval(next, 4000); }}
        function stopTimer()  {{ clearInterval(timer); }}

        outer.addEventListener('mouseenter', stopTimer);
        outer.addEventListener('mouseleave', startTimer);

        init();
        startTimer();
    </script>
</body>
</html>"""

components.html(html, height=260, scrolling=False)

st.divider()

# ── STEP 8: Price Spread + Seller Count ───────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()
    for _, row in df_stats_filtered.iterrows():
        color = CATEGORY_COLORS.get(row["Category"], "#FF6B6B")
        fig.add_trace(go.Bar(
            x=[row["Product"]],
            y=[row["Max Price (NZD)"] - row["Min Price (NZD)"]],
            base=row["Min Price (NZD)"],
            marker_color=color, opacity=0.4, showlegend=False,
            hovertemplate=(
                f"<b>{row['Product']}</b><br>"
                f"Min: NZD {row['Min Price (NZD)']:,.2f}<br>"
                f"Max: NZD {row['Max Price (NZD)']:,.2f}"
                f"<extra></extra>"
            )
        ))
        fig.add_trace(go.Scatter(
            x=[row["Product"]], y=[row["Avg Price (NZD)"]],
            mode="markers",
            marker=dict(size=10, color=color,
                       line=dict(width=2, color="white")),
            showlegend=False,
            hovertemplate=(
                f"<b>{row['Product']}</b><br>"
                f"Avg: NZD {row['Avg Price (NZD)']:,.2f}"
                f"<extra></extra>"
            )
        ))
    fig.update_layout(
        title="PRICE SPREAD PER PRODUCT", title_x=0.35,
        barmode="overlay", xaxis_tickangle=-45,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=400, yaxis_title="Price (NZD)"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        df_stats_filtered, x="Product", y="Seller Count", color="Category",
        title="SELLER COUNT PER PRODUCT",
        color_discrete_map=CATEGORY_COLORS,
        labels={"Seller Count": "Number of Sellers", "Product": ""}
    )
    fig.update_layout(
        title_x=0.35, xaxis_tickangle=-45,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.markdown(
    "<p style='text-align: center; color: gray; font-size: 12px;'>© 2026 Retail Price Intelligence Dashboard</p>",
    unsafe_allow_html=True
)