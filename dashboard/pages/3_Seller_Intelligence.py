import streamlit as st 
import plotly.express as px 
import plotly.graph_objects as go
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.db import run_query
from utils.queries import (
    SELLER_COUNT_PER_PRODUCT, CHEAPEST_SELLER_PER_PRODUCT,
    RATING_BY_SELLER, RATING_STATUS_DISTRIBUTION
)

from utils.sidebar import render_sidebar, BG_BASE64
from utils.styles import hide_streamlit_ui

CATEGORY_COLORS = {
    "laptop": "#667eea",
    "phone":  "#11998e",
    "camera": "#f7971e"
}

st.set_page_config(
    layout="wide"
)

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

st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
        <img src="app/static/seller-intelligence.png" width="42">
        <h1 style="margin: 0;">SELLER INTELLIGENCE</h1>
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

# ── SELLER INTELLIGENCE
df_count         = run_query(SELLER_COUNT_PER_PRODUCT)
df_rating_status = run_query(RATING_STATUS_DISTRIBUTION)

# ── CSS — only for animations, nothing else ────────────────────────────────────
st.markdown("""
    <style>
        @keyframes fadeInLeft {
            from { opacity: 0; transform: translateX(-20px); }
            to   { opacity: 1; transform: translateX(0); }
        }
        @keyframes pulseDot {
            0%   { transform: scale(1); opacity: 1; }
            50%  { transform: scale(1.4); opacity: 0.6; }
            100% { transform: scale(1); opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)

cat_colors = {
    "laptop": "#667eea",
    "phone":  "#11998e",
    "camera": "#f7971e"
}

rating_colors = {
    "verified": "#38ef7d",
    "unrated":  "#667eea",
    "limited":  "#FF6B6B"
}

col1, col2 = st.columns([3, 2])

# ── LEFT: Bars ─────────────────────────────────────────────────────────────────
with col1:
    max_count  = df_count["seller_count"].max()
    df_count_sorted = df_count.sort_values("seller_count", ascending=False)

    bars_html = """
        <p style='color: white; font-size: 13px; font-weight: 700;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px;
        padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08);
        text-align: center;'>
        Seller Count per Product</p>
    """

    for i, (_, row) in enumerate(df_count_sorted.iterrows()):
        pct   = (row["seller_count"] / max_count) * 100
        color = cat_colors.get(row["category"], "#667eea")
        bars_html += f"""
        <div style='display: flex; align-items: center; margin-bottom: 10px;'>
            <span style='color: white; font-size: 11px; font-weight: 600;
                         width: 130px; min-width: 130px; white-space: nowrap;
                         overflow: hidden; text-overflow: ellipsis;'>
                {row['product_name']}
            </span>
            <div style='flex: 1; background: rgba(255,255,255,0.06);
                        border-radius: 20px; height: 10px; margin: 0 10px;
                        overflow: hidden;'>
                <div style='width: {pct:.1f}%; height: 100%; border-radius: 20px;
                             background: linear-gradient(90deg, {color}, {color}99);'>
                </div>
            </div>
            <span style='color: gray; font-size: 11px; font-weight: 700;
                         width: 30px; text-align: right;'>
                {row['seller_count']}
            </span>
        </div>
        """

    # Category legend
    bars_html += "<div style='display: flex; gap: 16px; margin-top: 12px; justify-content: center;'>"
    for cat, color in cat_colors.items():
        bars_html += f"""
        <div style='display: inline-flex; align-items: center; gap: 6px;'>
            <div style='width: 10px; height: 10px; border-radius: 50%;
                        background: {color};'></div>
            <span style='color: gray; font-size: 11px;'>{cat}</span>
        </div>
        """
    bars_html += "</div>"

    st.markdown(bars_html, unsafe_allow_html=True)

# ── RIGHT: Donut + Legend ──────────────────────────────────────────────────────
with col2:
    st.markdown("""
        <p style='color: white; font-size: 13px; font-weight: 700;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px;
        padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08);
        text-align: center;'>
        Rating Status Distribution</p>
    """, unsafe_allow_html=True)

    total_count = df_rating_status["count"].sum()

    rating_colors = {
        "verified": "#38ef7d",
        "unrated":  "#667eea",
        "limited":  "#FF6B6B"
    }

    # ── Donut with spin animation ──────────────────────────────────────────────
    frames = []
    steps  = 20
    for i in range(steps + 1):
        angle = 90 + (270 * i / steps)  # spins from 90 to 360
        frames.append(go.Frame(
            data=[go.Pie(
                labels=df_rating_status["rating_status"],
                values=df_rating_status["count"],
                hole=0.60,
                rotation=angle,
                marker=dict(
                    colors=[rating_colors.get(s, "#999")
                            for s in df_rating_status["rating_status"]],
                    line=dict(color="#0e1117", width=3)
                ),
                textinfo="none",
                hovertemplate="<b>%{label}</b><br>%{value} listings (%{percent})<extra></extra>",
                sort=False
            )]
        ))

    fig = go.Figure(
        data=[go.Pie(
            labels=df_rating_status["rating_status"],
            values=df_rating_status["count"],
            hole=0.60,
            rotation=90,
            marker=dict(
                colors=[rating_colors.get(s, "#999")
                        for s in df_rating_status["rating_status"]],
                line=dict(color="#0e1117", width=3)
            ),
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value} listings (%{percent})<extra></extra>",
            sort=False
        )],
        frames=frames
    )

    fig.add_annotation(
        text=f"<b>{total_count}</b><br>listings",
        x=0.5, y=0.5,
        font=dict(size=18, color="white"),
        showarrow=False
    )

    fig.update_layout(
        height=260,
        margin=dict(t=10, b=10, l=20, r=20),
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

    # Auto-play via config
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    # ── Legend using st.columns — no HTML sanitizer issues ─────────────────────
    legend_df = df_rating_status.copy()
    legend_df["pct"] = (legend_df["count"] / total_count * 100).round(1)
    legend_df = legend_df.sort_values("count", ascending=False)

    for _, row in legend_df.iterrows():
        color = rating_colors.get(row["rating_status"], "#999")
        pct   = row["pct"]
        label = row["rating_status"].capitalize()
        count = row["count"]

        lcol, barcol, pctcol = st.columns([2, 5, 1])

        with lcol:
            st.markdown(
                f"<div style='display:flex; align-items:center; gap:6px; "
                f"padding-top:4px;'>"
                f"<div style='width:10px; height:10px; border-radius:50%; "
                f"background:{color}; flex-shrink:0;'></div>"
                f"<span style='color:white; font-size:11px; font-weight:600;'>"
                f"{label}</span></div>",
                unsafe_allow_html=True
            )

        with barcol:
            fig_bar = go.Figure(go.Bar(
                x=[pct],
                y=[""],
                orientation="h",
                marker=dict(color=color, opacity=0.85, line=dict(width=0)),
                hovertemplate=f"<b>{label}</b>: {count:,} listings<extra></extra>",
                showlegend=False
            ))
            fig_bar.update_layout(
                height=28,
                margin=dict(t=0, b=0, l=0, r=0),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(range=[0, 105], showticklabels=False,
                           showgrid=False, zeroline=False),
                yaxis=dict(showticklabels=False, showgrid=False)
            )
            st.plotly_chart(fig_bar, use_container_width=True,
                           config={"displayModeBar": False})

        with pctcol:
            st.markdown(
                f"<p style='color:gray; font-size:11px; "
                f"padding-top:4px; text-align:right;'>{pct}%</p>",
                unsafe_allow_html=True
            )

st.divider()

# Rating By Seller
# ── Rating + Cheapest Seller Section ──────────────────────────────────────────
df_rating        = run_query(RATING_BY_SELLER)
df_cheapest      = run_query(CHEAPEST_SELLER_PER_PRODUCT)

col1, col2 = st.columns(2)

# Top Rated Sellers 
with col1:
    st.markdown("""
        <p style='color: white; font-size: 13px; font-weight: 700;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px;
        padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08);
        text-align: center;'>
        Top Rated Sellers</p>
    """, unsafe_allow_html=True)

    if df_rating.empty:
        st.info("No rating data available yet.")
    else:
        df_top_rated = df_rating.nlargest(3, "avg_rating").sort_values(
            "avg_rating", ascending=True
        ).reset_index(drop=True)

        # ── Color by rating ────────────────────────────────────────────────────
        def get_color(rating):
            if rating >= 4.5: return "#38ef7d"
            elif rating >= 4.0: return "#f7971e"
            else: return "#FF6B6B"

        colors = [get_color(r) for r in df_top_rated["avg_rating"]]

        # ── Custom label: rating + reviews ─────────────────────────────────────
        labels = [
            f"  {row['avg_rating']:.1f} ★  ({row['total_reviews']:,} reviews)"
            for _, row in df_top_rated.iterrows()
        ]

        fig_rating = go.Figure()

        for i, (_, row) in enumerate(df_top_rated.iterrows()):
            color = get_color(row["avg_rating"])
            fig_rating.add_trace(go.Bar(
                x=[row["avg_rating"]],
                y=[row["seller"]],
                orientation="h",
                marker=dict(
                    color=color,
                    opacity=0.9,
                    line=dict(width=0),
                ),
                text=f"  {row['avg_rating']:.1f} ★   {row['total_reviews']:,} reviews",
                textposition="outside",
                textfont=dict(color="white", size=11),
                hovertemplate=(
                    f"<b>{row['seller']}</b><br>"
                    f"Rating: {row['avg_rating']:.1f}<br>"
                    f"Reviews: {row['total_reviews']:,}<br>"
                    f"Listings: {row['total_listings']}<extra></extra>"
                ),
                showlegend=False
            ))

        fig_rating.update_layout(
            height=420,
            margin=dict(t=20, b=20, l=10, r=220),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            bargap=0.35,
            xaxis=dict(
                range=[0, 7.5],
                showticklabels=False,
                showgrid=False,
                zeroline=False,
            ),
            yaxis=dict(
                showgrid=False,
                tickfont=dict(color="white", size=12),
                ticksuffix="  ",
            )
        )

        # Add medal annotations
        medals = ["🥉", "🥈", "🥇"]
        for i, (_, row) in enumerate(df_top_rated.iterrows()):
            fig_rating.add_annotation(
                x=0,
                y=row["seller"],
                text=medals[i],
                showarrow=False,
                xanchor="right",
                xshift=-8,
                font=dict(size=16),
            )

        st.plotly_chart(
            fig_rating,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        # ── Legend ─────────────────────────────────────────────────────────────
        leg_col1, leg_col2, leg_col3 = st.columns(3)
        with leg_col1:
            st.markdown(
                "<div style='display:flex; align-items:center; gap:6px; justify-content:center;'>"
                "<div style='width:8px; height:8px; border-radius:50%; background:#38ef7d;'></div>"
                "<span style='color:rgba(255,255,255,0.5); font-size:10px;'>≥ 4.5 Excellent</span></div>",
                unsafe_allow_html=True
            )
        with leg_col2:
            st.markdown(
                "<div style='display:flex; align-items:center; gap:6px; justify-content:center;'>"
                "<div style='width:8px; height:8px; border-radius:50%; background:#f7971e;'></div>"
                "<span style='color:rgba(255,255,255,0.5); font-size:10px;'>≥ 4.0 Good</span></div>",
                unsafe_allow_html=True
            )
        with leg_col3:
            st.markdown(
                "<div style='display:flex; align-items:center; gap:6px; justify-content:center;'>"
                "<div style='width:8px; height:8px; border-radius:50%; background:#FF6B6B;'></div>"
                "<span style='color:rgba(255,255,255,0.5); font-size:10px;'>< 4.0 Fair</span></div>",
                unsafe_allow_html=True
            )

# ── RIGHT: Cheapest Seller per Product ────────────────────────────────────────
with col2:
    st.markdown("""
        <p style='color: white; font-size: 13px; font-weight: 700;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px;
        padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08);
        text-align: center;'>
        Cheapest Seller per Category</p>
    """, unsafe_allow_html=True)

    df_cheapest = run_query("""
        WITH ranked AS (
            SELECT
                product_name,
                category,
                seller,
                price,
                AVG(price) OVER (PARTITION BY category) AS avg_price,
                ROW_NUMBER() OVER (
                    PARTITION BY category
                    ORDER BY price ASC
                ) AS rn
            FROM dev_staging.stg_electronic_products
            WHERE snapshot_date = (
                SELECT MAX(snapshot_date)
                FROM dev_staging.stg_electronic_products
            )
        )
        SELECT
            category,
            product_name,
            seller,
            ROUND(price::numeric, 2)     AS min_price,
            ROUND(avg_price::numeric, 2) AS avg_price,
            ROUND(((avg_price - price) / avg_price * 100)::numeric, 1) AS savings_pct
        FROM ranked
        WHERE rn = 1
        ORDER BY category
    """)

    if df_cheapest.empty:
        st.info("No pricing data available yet.")
    else:
        max_price = df_cheapest["min_price"].max()

        for _, row in df_cheapest.iterrows():
            color = CATEGORY_COLORS.get(row["category"], "#667eea")
            pct   = (row["min_price"] / max_price) * 100

            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #1a1d2e, #1E2130);
                    border-radius: 12px;
                    padding: 16px 18px;
                    margin-bottom: 12px;
                    border-left: 3px solid {color};
                '>
                    <table style='width: 100%; border-collapse: collapse;
                                  margin-bottom: 10px;'>
                        <tr>
                            <td style='color: {color}; font-size: 11px;
                                       font-weight: 700; letter-spacing: 1.5px;
                                       padding: 0 0 6px 0;'>
                                {row['category'].upper()}
                            </td>
                            <td style='text-align: right; padding: 0 0 6px 0;
                                       color: #38ef7d; font-size: 11px;
                                       font-weight: 700;'>
                                💚 Save {row['savings_pct']}%
                            </td>
                        </tr>
                        <tr>
                            <td style='color: white; font-size: 13px;
                                       font-weight: 700; padding: 0 0 2px 0;'>
                                {row['product_name']}
                            </td>
                            <td style='text-align: right; color: #38ef7d;
                                       font-size: 18px; font-weight: 800;
                                       padding: 0;'>
                                NZD {row['min_price']:,.2f}
                            </td>
                        </tr>
                        <tr>
                            <td style='color: gray; font-size: 11px; padding: 0;'>
                                via {row['seller']}
                            </td>
                            <td style='text-align: right; color: gray;
                                       font-size: 10px; padding: 0;'>
                                Avg: NZD {row['avg_price']:,.2f}
                            </td>
                        </tr>
                    </table>
                    <div style='background: rgba(255,255,255,0.06);
                                border-radius: 20px; height: 5px; overflow: hidden;'>
                        <div style='width: {pct:.1f}%; height: 100%;
                                    border-radius: 20px;
                                    background: linear-gradient(90deg, {color}, {color}88);'>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)


st.divider()

st.markdown(
    "<p style='text-align: center; color: gray; font-size: 12px;'>© 2026 Retail Price Intelligence Dashboard  </p>",
    unsafe_allow_html=True
)
