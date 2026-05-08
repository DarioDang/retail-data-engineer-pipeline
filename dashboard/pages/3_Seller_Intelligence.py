import streamlit as st 
import plotly.express as px 
import plotly.graph_objects as go
import streamlit.components.v1 as components
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

# Header
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
        <img src="app/static/seller-intelligence.png" width="42" class="page-title-icon"/>
        <h1 class="page-title-text">SELLER INTELLIGENCE</h1>
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
df_rating   = run_query(RATING_BY_SELLER)
df_cheapest = run_query(CHEAPEST_SELLER_PER_PRODUCT)

# ── Build HTML for both columns ────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <p style='color:white; font-size:13px; font-weight:700;
        letter-spacing:2px; text-transform:uppercase; margin-bottom:16px;
        padding-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.08);
        text-align:center;'>Top Rated Sellers</p>
    """, unsafe_allow_html=True)

    if df_rating.empty:
        st.info("No rating data available yet.")
    else:
        df_top_rated = df_rating.nlargest(3, "avg_rating").sort_values(
            "avg_rating", ascending=False
        ).reset_index(drop=True)

        # Build all cards as one HTML block
        cards_html = """
        <style>
            @keyframes shimmerCard {
                0%   { left: -100%; }
                100% { left: 200%; }
            }
            @keyframes pulseBar {
                0%,100% { opacity: 0.7; }
                50%      { opacity: 1; }
            }
            @keyframes floatBadge {
                0%,100% { transform: translateY(0px); }
                50%      { transform: translateY(-2px); }
            }
            @keyframes scanLine {
                0%   { top: -40%; }
                100% { top: 140%; }
            }
            @keyframes barFlow {
                0%   { background-position: 0% 50%; }
                100% { background-position: 200% 50%; }
            }
        </style>
        """

        for idx, row in df_top_rated.iterrows():
            rank = idx + 1

            if row["avg_rating"] >= 4.5:
                color = "#38ef7d"; rgba = "56,239,125"; badge = "EXCELLENT"
            elif row["avg_rating"] >= 4.0:
                color = "#f7971e"; rgba = "247,151,30"; badge = "GOOD"
            else:
                color = "#FF6B6B"; rgba = "255,107,107"; badge = "FAIR"

            full_stars = int(row["avg_rating"])
            stars_html = "★" * full_stars + "☆" * (5 - full_stars)
            bar_width  = (row["avg_rating"] / 5.0) * 100
            medal      = ["🥇","🥈","🥉"][rank-1]
            anim_delay = f"{idx * 0.3}s"

            cards_html += f"""
            <div style='
                background: linear-gradient(135deg, #1a1d2e, #1E2130);
                border-radius: 12px;
                padding: 14px 16px;
                margin-bottom: 10px;
                border-left: 3px solid {color};
                min-height: 110px;
                position: relative;
                overflow: hidden;
                transition: transform 0.25s ease, box-shadow 0.25s ease;
                animation: none;
            '
            onmouseover="this.style.transform='translateX(4px)';this.style.boxShadow='0 8px 24px rgba({rgba},0.2)';"
            onmouseout="this.style.transform='translateX(0)';this.style.boxShadow='';">

                <!-- Scan line animation -->
                <div style='
                    position: absolute;
                    left: 0; right: 0;
                    height: 35%;
                    background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.025), transparent);
                    animation: scanLine 4s linear {anim_delay} infinite;
                    pointer-events: none;
                    top: -40%;
                '></div>

                <!-- Shimmer -->
                <div style='
                    position: absolute;
                    top: 0; height: 100%; width: 50%;
                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.02), transparent);
                    animation: shimmerCard 3s ease-in-out {anim_delay} infinite;
                    pointer-events: none;
                    left: -100%;
                '></div>

                <div style='display:flex; align-items:center; gap:12px; position:relative;'>
                    <div style='font-size:22px; min-width:30px; text-align:center;'>{medal}</div>

                    <div style='flex:1; min-width:0;'>
                        <div style='display:flex; justify-content:space-between;
                            align-items:center; margin-bottom:6px;'>
                            <span style='color:white; font-size:13px; font-weight:700;
                                white-space:nowrap; overflow:hidden;
                                text-overflow:ellipsis; max-width:160px;
                                display:block;'>{row['seller']}</span>
                            <span style='
                                background:rgba({rgba},0.15);
                                border:1px solid {color};
                                border-radius:6px; padding:2px 8px;
                                color:{color}; font-size:9px; font-weight:700;
                                letter-spacing:1px; margin-left:8px;
                                white-space:nowrap; display:inline-block;
                                animation: floatBadge 2.5s ease-in-out {anim_delay} infinite;
                            '>{badge}</span>
                        </div>

                        <div style='display:flex; align-items:center;
                            gap:6px; margin-bottom:8px;'>
                            <span style='color:{color}; font-size:13px;
                                letter-spacing:1px;'>{stars_html}</span>
                            <span style='color:{color}; font-size:13px;
                                font-weight:800;'>{row['avg_rating']:.1f}</span>
                            <span style='color:rgba(255,255,255,0.3);
                                font-size:10px;'>({row['total_reviews']:,} reviews)</span>
                        </div>

                        <div style='background:rgba(255,255,255,0.06);
                            border-radius:20px; height:3px; overflow:hidden;'>
                            <div style='
                                width:{bar_width:.1f}%; height:100%;
                                border-radius:20px;
                                background: linear-gradient(90deg, {color}, {color}44, {color});
                                background-size: 200% 100%;
                                animation: barFlow 2s linear infinite, pulseBar 2s ease-in-out infinite;
                            '></div>
                        </div>
                    </div>
                </div>
            </div>
            """

        components.html(cards_html, height=420, scrolling=False)

with col2:
    st.markdown("""
        <p style='color:white; font-size:13px; font-weight:700;
        letter-spacing:2px; text-transform:uppercase; margin-bottom:16px;
        padding-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.08);
        text-align:center;'>Cheapest Seller per Category</p>
    """, unsafe_allow_html=True)

    df_cheapest = run_query("""
        WITH ranked AS (
            SELECT product_name, category, seller, price,
                AVG(price) OVER (PARTITION BY category) AS avg_price,
                ROW_NUMBER() OVER (PARTITION BY category ORDER BY price ASC) AS rn
            FROM dev_staging.stg_electronic_products
            WHERE snapshot_date = (
                SELECT MAX(snapshot_date) FROM dev_staging.stg_electronic_products
            )
        )
        SELECT category, product_name, seller,
            ROUND(price::numeric, 2) AS min_price,
            ROUND(avg_price::numeric, 2) AS avg_price,
            ROUND(((avg_price - price) / avg_price * 100)::numeric, 1) AS savings_pct
        FROM ranked WHERE rn = 1 ORDER BY category
    """)

    if df_cheapest.empty:
        st.info("No pricing data available yet.")
    else:
        max_price  = df_cheapest["min_price"].max()

        cheap_html = """
        <style>
            @keyframes shimmerCard2 {
                0%   { left: -100%; }
                100% { left: 200%; }
            }
            @keyframes scanLine2 {
                0%   { top: -40%; }
                100% { top: 140%; }
            }
            @keyframes barFlow2 {
                0%   { background-position: 0% 50%; }
                100% { background-position: 200% 50%; }
            }
            @keyframes priceGlow {
                0%,100% { text-shadow: 0 0 0px rgba(56,239,125,0); }
                50%      { text-shadow: 0 0 12px rgba(56,239,125,0.7); }
            }
            @keyframes savingsPulse {
                0%,100% { opacity: 0.8; }
                50%      { opacity: 1; transform: scale(1.03); }
            }
        </style>
        """

        for i, (_, row) in enumerate(df_cheapest.iterrows()):
            color     = CATEGORY_COLORS.get(row["category"], "#667eea")
            hex_color = color.lstrip("#")
            r         = int(hex_color[0:2], 16)
            g         = int(hex_color[2:4], 16)
            b         = int(hex_color[4:6], 16)
            pct       = (row["min_price"] / max_price) * 100
            delay     = f"{i * 0.3}s"

            cheap_html += f"""
            <div style='
                background: linear-gradient(135deg, #1a1d2e, #1E2130);
                border-radius: 12px;
                padding: 16px 18px;
                margin-bottom: 10px;
                border-left: 3px solid {color};
                min-height: 110px;
                position: relative;
                overflow: hidden;
                transition: transform 0.25s ease, box-shadow 0.25s ease;
            '
            onmouseover="this.style.transform='translateX(4px)';this.style.boxShadow='0 8px 24px rgba({r},{g},{b},0.2)';"
            onmouseout="this.style.transform='translateX(0)';this.style.boxShadow='';">

                <!-- Scan line -->
                <div style='
                    position:absolute; left:0; right:0; height:35%;
                    background:linear-gradient(to bottom,transparent,rgba(255,255,255,0.025),transparent);
                    animation:scanLine2 4s linear {delay} infinite;
                    pointer-events:none; top:-40%;
                '></div>

                <!-- Shimmer -->
                <div style='
                    position:absolute; top:0; height:100%; width:50%;
                    background:linear-gradient(90deg,transparent,rgba(255,255,255,0.02),transparent);
                    animation:shimmerCard2 3s ease-in-out {delay} infinite;
                    pointer-events:none; left:-100%;
                '></div>

                <div style='position:relative;'>
                    <div style='display:flex; justify-content:space-between;
                        align-items:center; margin-bottom:6px;'>
                        <span style='color:{color}; font-size:11px; font-weight:700;
                            letter-spacing:1.5px;'>{row['category'].upper()}</span>
                        <span style='
                            color:#38ef7d; font-size:11px; font-weight:700;
                            animation:savingsPulse 2.5s ease-in-out {delay} infinite;
                            display:inline-block;
                        '>💚 Save {row['savings_pct']}%</span>
                    </div>

                    <div style='display:flex; justify-content:space-between;
                        align-items:center; margin-bottom:4px;'>
                        <span style='color:white; font-size:13px;
                            font-weight:700;'>{row['product_name']}</span>
                        <span style='
                            color:#38ef7d; font-size:18px; font-weight:800;
                            animation:priceGlow 2.5s ease-in-out {delay} infinite;
                            display:inline-block;
                        '>NZD {row['min_price']:,.2f}</span>
                    </div>

                    <div style='display:flex; justify-content:space-between;
                        align-items:center; margin-bottom:10px;'>
                        <span style='color:gray; font-size:11px;'>via {row['seller']}</span>
                        <span style='color:gray; font-size:10px;'>
                            Avg: NZD {row['avg_price']:,.2f}
                        </span>
                    </div>

                    <div style='background:rgba(255,255,255,0.06);
                        border-radius:20px; height:4px; overflow:hidden;'>
                        <div style='
                            width:{pct:.1f}%; height:100%; border-radius:20px;
                            background:linear-gradient(90deg,{color},{color}44,{color});
                            background-size:200% 100%;
                            animation:barFlow2 2s linear {delay} infinite;
                        '></div>
                    </div>
                </div>
            </div>
            """

        components.html(cheap_html, height=420, scrolling=False)

st.divider()

st.markdown(
    "<p style='text-align: center; color: gray; font-size: 12px;'>© 2026 Retail Price Intelligence Dashboard  </p>",
    unsafe_allow_html=True
)
