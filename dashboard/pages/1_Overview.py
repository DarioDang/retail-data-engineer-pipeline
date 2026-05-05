import streamlit as st 
import plotly.express as px 
import sys 
import pandas as pd 
import plotly.graph_objects as go
from utils.queries import AVG_PRICE_OVER_TIME, DISCOUNT_PRODUCTS
from utils.sidebar import render_sidebar
from utils.styles import hide_streamlit_ui
from PIL import Image
import os 
sys.path.append("..")
from utils.sidebar import render_sidebar, BG_BASE64

# Load custom icon
icon_path = os.path.join(os.path.dirname(__file__), "..", "static", "overview.png")
icon = Image.open(icon_path)
from utils.db import run_query
from utils.queries import (
    TOTAL_LISTINGS, TOTAL_PRODUCTS, TOTAL_SELLERS,CATEGORY_SUMMARY
)

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

# Hide the background streamlit 
hide_streamlit_ui

st.markdown(
    """
    <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
    ">
        <img src="app/static/overview.png" width="42">
        <h1 style="margin: 0;">OVERVIEW DASHBOARD</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
        h1 { text-align: center; }
        h2 { text-align: center; }
        h3 { text-align: center; }
        [data-testid="stMetricLabel"] { text-align: center; }
        [data-testid="stMetricValue"] { text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <p style='text-align: center; color: gray; font-size: 14px;'>
        High-level summary of all products and sellers
    </p>
""", unsafe_allow_html=True)

# ── METRIC CARDS SECTION ───────────────────────────────────────────

# Query all data
total    = run_query(TOTAL_LISTINGS)
products = run_query(TOTAL_PRODUCTS)
sellers  = run_query(TOTAL_SELLERS)
df_discount = run_query(DISCOUNT_PRODUCTS)

total_listings = f"{total['total'][0]:,}"
total_products = str(products['total'][0])
total_sellers  = str(sellers['total'][0])

# Discount metrics
if not df_discount.empty:
    total_discounted = str(len(df_discount))
    avg_discount     = f"{df_discount['discount_pct'].mean().round(1)}%"
    max_discount     = f"{df_discount['discount_pct'].max()}%"
else:
    total_discounted = "0"
    avg_discount     = "0%"
    max_discount     = "0%"

# ── Shared CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
        .metric-card {
            border-radius: 16px;
            padding: 32px 24px;
            margin: 8px 0;
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 200px;
        }
        .metric-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.4);
        }
        .metric-card-blue   { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .metric-card-green  { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
        .metric-card-orange { background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%); }
        .metric-card-red    { background: linear-gradient(135deg, #FF6B6B 0%, #ee0979 100%); }
        .metric-card-teal   { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
        .metric-card-pink   { background: linear-gradient(135deg, #f953c6 0%, #b91d73 100%); }
        .metric-icon  { font-size: 52px; margin-bottom: 16px; }
        .metric-value { font-size: 56px; font-weight: 800; color: white; margin: 0; line-height: 1; }
        .metric-label { font-size: 18px; color: rgba(255,255,255,0.9); margin-top: 10px; font-weight: 600; letter-spacing: 1px; }
        .sparkline-top    { position: absolute; top: 0; left: 0; width: 100%; opacity: 0.25; }
        .sparkline-bottom { position: absolute; bottom: 0; left: 0; width: 100%; opacity: 0.25; }
        @keyframes moveWave {
            0%   { transform: translateX(0px); }
            50%  { transform: translateX(-20px); }
            100% { transform: translateX(0px); }
        }
        .sparkline-top svg,
        .sparkline-bottom svg { animation: moveWave 3s ease-in-out infinite; }
    </style>
""", unsafe_allow_html=True)

# ── Shared Sparkline Templates ─────────────────────────────────────────────────
# Smooth wave — for metric cards
WAVE_TOP = (
    "<div class='sparkline-top'><svg viewBox='0 0 300 40' xmlns='http://www.w3.org/2000/svg'>"
    "<polyline points='0,30 30,20 60,25 90,10 120,20 150,15 180,25 210,10 240,20 270,15 300,25'"
    " fill='none' stroke='white' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/>"
    "</svg></div>"
)
WAVE_BOTTOM = (
    "<div class='sparkline-bottom'><svg viewBox='0 0 300 40' xmlns='http://www.w3.org/2000/svg'>"
    "<polyline points='0,10 30,20 60,15 90,30 120,20 150,25 180,15 210,30 240,20 270,25 300,15'"
    " fill='none' stroke='white' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/>"
    "</svg></div>"
)

# ── Row 1: Listing Metrics ─────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        "<div class='metric-card metric-card-blue'>"
        + WAVE_TOP
        + "<div class='metric-icon'><img src='app/static/total-listing.png' width='52' height='52'/></div>"
        + f"<p class='metric-value'>{total_listings}</p>"
        + "<p class='metric-label'>TOTAL LISTINGS</p>"
        + WAVE_BOTTOM
        + "</div>",
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        "<div class='metric-card metric-card-green'>"
        + WAVE_TOP
        + "<div class='metric-icon'><img src='app/static/total-products.png' width='52' height='52'/></div>"
        + f"<p class='metric-value'>{total_products}</p>"
        + "<p class='metric-label'>TOTAL PRODUCTS</p>"
        + WAVE_BOTTOM
        + "</div>",
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        "<div class='metric-card metric-card-orange'>"
        + WAVE_TOP
        + "<div class='metric-icon'><img src='app/static/total-sellers.png' width='52' height='52'/></div>"
        + f"<p class='metric-value'>{total_sellers}</p>"
        + "<p class='metric-label'>TOTAL SELLERS</p>"
        + WAVE_BOTTOM
        + "</div>",
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

# ── Row 2: Discount Metrics ────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        "<div class='metric-card metric-card-red'>"
        + WAVE_TOP
        + "<div class='metric-icon'><img src='app/static/total-discounted-icon.png' width='52' height='52'/></div>"
        + f"<p class='metric-value'>{total_discounted}</p>"
        + "<p class='metric-label'>TOTAL DISCOUNTED</p>"
        + WAVE_BOTTOM
        + "</div>",
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        "<div class='metric-card metric-card-teal'>"
        + WAVE_TOP
        + "<div class='metric-icon'><img src='app/static/average-discount-icon.png' width='52' height='52'/></div>"
        + f"<p class='metric-value'>{avg_discount}</p>"
        + "<p class='metric-label'>AVG DISCOUNT</p>"
        + WAVE_BOTTOM
        + "</div>",
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        "<div class='metric-card metric-card-pink'>"
        + WAVE_TOP
        + "<div class='metric-icon'><img src='app/static/biggest-discount-icon.png' width='52' height='52'/></div>"
        + f"<p class='metric-value'>{max_discount}</p>"
        + "<p class='metric-label'>BIGGEST DISCOUNT</p>"
        + WAVE_BOTTOM
        + "</div>",
        unsafe_allow_html=True
    )

st.divider()

# Category Summary Table
st.subheader("CATEGORY SUMMARY")
df_summary = run_query(CATEGORY_SUMMARY)
df_summary.columns = [
    "Category", "Products", "Sellers",
    "Total Listings", "Min Price (NZD)",
    "Max Price (NZD)", "Avg Price (NZD)"
]

# Spacer 
st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)

# ── Row 2: Charts ──────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

CATEGORY_COLORS = {
    "laptop": "#667eea",
    "phone":  "#11998e",
    "camera": "#f7971e"
}

with col1:
    st.markdown("""
        <p style='color: white; font-size: 14px; font-weight: 700;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;
        padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08);
        text-align: center;'>
        AVERAGE PRICE BY CATEGORIES</p>
    """, unsafe_allow_html=True)
    # Average price by category bar chart
    fig = px.bar(
        df_summary,
        x="Category",
        y="Avg Price (NZD)",
        color="Category",
        title=" ",
        color_discrete_map={
            "laptop": "#667eea",
            "phone":  "#11998e",
            "camera": "#f7971e"
        },
        labels={"Avg Price (NZD)": "Avg Price (NZD)", "Category": ""}
    )
    fig.update_layout(
        title_x=0.35,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("""
        <p style='color: white; font-size: 14px; font-weight: 700;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;
        padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08);
        text-align: center;'>
        Listings Distribution</p>
    """, unsafe_allow_html=True)

    # Spacer 
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

    total_listings = df_summary["Total Listings"].sum()

    # ── Animated donut with percent labels inside ──────────────────────────────
    donut_frames = []
    steps = 20
    for i in range(steps + 1):
        angle = 90 + (360 * i / steps)
        donut_frames.append(go.Frame(
            data=[go.Pie(
                labels=[r["Category"].capitalize() for _, r in df_summary.iterrows()],
                values=df_summary["Total Listings"],
                hole=0.60,
                rotation=angle,
                marker=dict(
                    colors=[CATEGORY_COLORS.get(c, "#999") for c in df_summary["Category"]],
                    line=dict(color="#0e1117", width=3)
                ),
                textinfo="percent",
                textposition="inside",
                textfont=dict(size=12, color="white"),
                hovertemplate="<b>%{label}</b><br>%{value} listings (%{percent})<extra></extra>",
                sort=False
            )]
        ))

    fig2 = go.Figure(
        data=[go.Pie(
            labels=[r["Category"].capitalize() for _, r in df_summary.iterrows()],
            values=df_summary["Total Listings"],
            hole=0.60,
            rotation=90,
            marker=dict(
                colors=[CATEGORY_COLORS.get(c, "#999") for c in df_summary["Category"]],
                line=dict(color="#0e1117", width=3)
            ),
            textinfo="percent",
            textposition="inside",
            textfont=dict(size=12, color="white"),
            hovertemplate="<b>%{label}</b><br>%{value} listings (%{percent})<extra></extra>",
            sort=False
        )],
        frames=donut_frames
    )

    fig2.add_annotation(
        text=f"<b>{total_listings:,}",
        x=0.5, y=0.5,
        font=dict(size=16, color="white"),
        showarrow=False
    )

    fig2.update_layout(
        height=260,
        margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            visible=False,
            buttons=[dict(
                method="animate",
                args=[None, dict(
                    frame=dict(duration=30, redraw=True),
                    transition=dict(duration=0),
                    fromcurrent=True,
                    mode="immediate"
                )]
            )]
        )]
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # Spacer 
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

    # ── Simple legend — dot + label only using st.columns ─────────────────────
    leg_cols = st.columns(len(df_summary))
    for col, (_, row) in zip(leg_cols, df_summary.iterrows()):
        color = CATEGORY_COLORS.get(row["Category"], "#999")
        with col:
            st.markdown(
                f"<div style='display: flex; align-items: center; "
                f"justify-content: center; gap: 6px;'>"
                f"<div style='width: 10px; height: 10px; border-radius: 50%; "
                f"background: {color}; flex-shrink: 0;'></div>"
                f"<span style='color: white; font-size: 12px; font-weight: 600;'>"
                f"{row['Category'].capitalize()}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

# ── Row 3: Price Range Chart (Weekly)
df_trend = run_query(AVG_PRICE_OVER_TIME)
df_trend["snapshot_date"] = pd.to_datetime(df_trend["snapshot_date"])
total_days = df_trend["snapshot_date"].nunique()

if total_days < 14:
    # ── Daily view ─────────────────────────────────────────────────────────────
    df_trend["day"]       = df_trend["snapshot_date"].dt.date
    df_trend["day_label"] = df_trend["snapshot_date"].dt.strftime("%d %b")

    df_category_trend = df_trend.groupby(
        ["day", "day_label", "category"]
    )["avg_price"].mean().reset_index()
    df_category_trend["avg_price"] = df_category_trend["avg_price"].round(2)
    df_category_trend = df_category_trend.sort_values("day")
    df_category_trend["week"] = df_category_trend["day_label"]
    ordered_labels = df_category_trend["day_label"].unique().tolist()

    view_label = "Daily"
    note = f"(Weekly view activates after 14 days of data — currently {total_days}d)"

else:
    # ── Weekly view ────────────────────────────────────────────────────────────
    df_trend["week_start"] = df_trend["snapshot_date"].dt.to_period("W").apply(
        lambda r: r.start_time
    )
    df_trend["week_label"] = df_trend["week_start"].dt.strftime("%d %b")

    df_category_trend = df_trend.groupby(
        ["week_start", "week_label", "category"]
    )["avg_price"].mean().reset_index()
    df_category_trend["avg_price"] = df_category_trend["avg_price"].round(2)
    df_category_trend = df_category_trend.sort_values("week_start")
    df_category_trend["week"] = df_category_trend["week_label"]
    ordered_labels = df_category_trend["week_label"].unique().tolist()

    view_label = "Weekly"
    note = ""

# ── Chart ──────────────────────────────────────────────────────────────────────
fig = px.line(
    df_category_trend,
    x="week",
    y="avg_price",
    color="category",
    markers=True,
    labels={
        "week": "Period",
        "avg_price": "Avg Price (NZD)",
        "category": "Category"
    },
    color_discrete_map={
        "laptop": "#667eea",
        "phone":  "#11998e",
        "camera": "#f7971e"
    }
)

fig.update_layout(
    title=dict(
        text=f"AVERAGE PRICE TREND BY CATEGORY — {view_label.upper()} VIEW",
        x=0.5,
        xanchor="center",
        font=dict(size=14, color="white")
    ),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    hovermode="x unified",
    xaxis=dict(
        type="category",
        tickangle=-45,
        tickmode="array",
        tickvals=ordered_labels,
        categoryorder="array",
        categoryarray=ordered_labels,
        tickfont=dict(size=10, color="rgba(255,255,255,0.5)"),
        gridcolor="rgba(255,255,255,0.03)",
    ),
    yaxis=dict(
        tickprefix="$",
        tickfont=dict(size=10, color="rgba(255,255,255,0.5)"),
        gridcolor="rgba(255,255,255,0.05)",
    ),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=1.15,
        xanchor="left",
        x=0,
        title_text="",
        font=dict(color="rgba(255,255,255,0.6)", size=11)
    ),
    margin=dict(t=80, b=10, l=10, r=10),
    height=350,
)

fig.update_traces(line_width=2.5)

st.plotly_chart(fig, use_container_width=True)
if note:
    st.markdown(f"""
        <p style='color: rgba(255,255,255,0.3); font-size: 10px;
            text-align: center; margin-top: -16px;'>{note}</p>
    """, unsafe_allow_html=True)

st.divider()

# Copyright
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 12px;'>© 2026 Retail Price Intelligence Dashboard  </p>",
    unsafe_allow_html=True
)
