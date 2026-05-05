import streamlit as st 
from PIL import Image
import os 
import base64
from utils.sidebar import render_sidebar

# Load custom icon
icon_path = os.path.join(os.path.dirname(__file__), "static", "retail-headpage.png")
icon = Image.open(icon_path)

st.set_page_config(
    page_title="Retail Price Intelligence",
    page_icon=icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Load background image
bg_path = os.path.join(os.path.dirname(__file__), "image", "background", "background-1.jpg")
bg_base64 = get_base64_image(bg_path)

# Global CSS
st.markdown(f"""
    <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpeg;base64,{bg_base64}");
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
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0e1117 0%, #1a1d2e 50%, #1E2130 100%) !important;
        }}
        [data-testid="stHeader"] {{
            background: rgba(14, 17, 23, 0.8);
            backdrop-filter: blur(10px);
        }}
        h1 {{ text-align: center; }}
        h2 {{ text-align: center; }}
        h3 {{ text-align: center; }}
        .stCaption {{ text-align: center; }}
        .section-card {{
            background-color: #1E2130;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            min-height: 320px;
            display: flex;
            flex-direction: column;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }}
        .section-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 10px 30px rgba(255, 107, 107, 0.3);
            background-color: #252840;
        }}
    </style>
""", unsafe_allow_html=True)

# Add the sidebar 
render_sidebar()

# Header 

st.markdown("""
    <style>
        @keyframes gradientShift {
            0%   { background-position: 0% 50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-20px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes expandLine {
            from { width: 0%; }
            to   { width: 60px; }
        }
        .section-title-wrapper {
            text-align: center;
            margin: 20px 0 24px 0;
            animation: fadeInDown 0.8s ease forwards;
        }
        .section-title-badge {
            display: inline-block;
            background: rgba(255,107,107,0.1);
            border: 1px solid rgba(255,107,107,0.3);
            border-radius: 20px;
            padding: 4px 14px;
            color: #FF6B6B;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 12px;
        }
        .section-title-main {
            font-size: 36px;
            font-weight: 800;
            letter-spacing: 3px;
            background: linear-gradient(270deg, #FF6B6B, #667eea, #11998e, #f7971e, #FF6B6B);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientShift 4s ease infinite;
            margin: 0;
        }      
        .section-title-underline {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin: 10px 0 12px 0;
            transform: translateX(-20px);
        }
        .underline-bar {
            height: 2px;
            width: 60px;
            background: linear-gradient(90deg, transparent, #FF6B6B);
            border-radius: 2px;
            animation: expandLine 1s ease forwards;
        }
        .underline-bar-right {
            background: linear-gradient(90deg, #FF6B6B, transparent);
        }
        .underline-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #FF6B6B;
        }
        .section-title-sub {
            color: #8892a4;
            font-size: 14px;
            margin: 0;
            letter-spacing: 0.5px;
        }
    </style>
    
    <div class='section-title-wrapper'>
        <h2 class='section-title-main'>RETAIL PRICE DASHBOARD</h2>
        <div class='section-title-underline'>
            <div class='underline-bar'></div>
            <div class='underline-dot'></div>
            <div class='underline-bar underline-bar-right'></div>
        </div>
        <p style='color: gray; font-size: 16px; text-align: center;'>
            Monitor and analyze product prices across retailers in New Zealand
        </p>
        <br>
        <p style='text-align: center; color: gray; font-size: 14px;'>
            <img src='app/static/google-shopping.png' width='20'/> Google Shopping &nbsp;|&nbsp; 
            <img src='app/static/products.png' width='20'/> 8 Products &nbsp;|&nbsp; 
            <img src='app/static/daily-update.png' width='20'/> Daily Updates &nbsp;|&nbsp; 
            <img src='app/static/new-zealand-flag.png' width='20'/> New Zealand
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# About Dashboard Section
st.markdown("""
    <div style='
        border-left: 3px solid #FF6B6B;
        padding-left: 12px;
        margin-bottom: 16px;
    '>
        <p style='
            color: rgba(255,255,255,0.85);
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            margin: 0;
        '>About This Dashboard</p>
    </div>
""", unsafe_allow_html=True)

text_col, img_col = st.columns([3, 1])

with text_col:
    st.markdown("""
        <p style='color: gray; text-align: justify; line-height: 1.8; font-size: 14px;'>
            This dashboard tracks and analyzes real-time product prices from Google Shopping 
            across 8 popular consumer electronics in New Zealand, covering laptops, smartphones, 
            and action cameras from leading brands like Apple, Samsung, Dell, HP, GoPro, and DJI.
        </p>
        <p style='color: gray; text-align: justify; line-height: 1.8; font-size: 14px;'>
            Built as a end-to-end data engineering portfolio project, the pipeline is designed 
            to demonstrate modern data engineering practices including data ingestion, 
            transformation, storage, orchestration, and visualization, all running on 
            a fully automated daily schedule.
        </p>
        <p style='color: gray; text-align: justify; line-height: 1.8; font-size: 14px;'>
            Data is collected daily via SerpAPI and loaded into AWS S3 as a data lake using 
            dlt (data load tool). From there, data is loaded into a PostgreSQL warehouse, 
            transformed using dbt and orchestrated end-to-end with Kestra.
        </p>
        <p style='color: gray; text-align: justify; line-height: 1.8; font-size: 14px;'>
            The goal of this project is to provide actionable price intelligence which  helping 
            consumers identify the cheapest sellers, track price trends over time, monitor 
            discount patterns, and understand seller competition across the New Zealand 
            electronics market.
        </p>
        <p style='color: gray; text-align: justify; line-height: 1.8; font-size: 14px;'>
            This dashboard was created as part of the Data Engineering Zoomcamp 2026 cohort, 
            demonstrating skills across the full data engineering stack from raw API 
            ingestion through to an interactive analytics dashboard built with Streamlit.
        </p>
    """, unsafe_allow_html=True)

with img_col:
    img_path = os.path.join(os.path.dirname(__file__), "image", "homepage", "about_us.png")
    st.image(img_path, use_container_width=True)

st.divider()

# How It Works
st.markdown("""
    <div style='text-align: center; margin-bottom: 24px;'>
        <span style='
            background: linear-gradient(90deg, #FF6B6B, #f7971e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 9px;
            font-weight: 800;
            letter-spacing: 4px;
            text-transform: uppercase;
            display: block;
            margin-bottom: 8px;
        '>NAVIGATION GUIDE</span>
        <p style='
            background: linear-gradient(270deg, #FF6B6B, #667eea, #11998e, #f7971e, #FF6B6B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 30px;
            font-weight: 800;
            margin: 0 0 8px 0;
            letter-spacing: 0.5px;
            text-align: center;
        '>How It Works</p>
        <p style='
            color: rgba(255,255,255,0.4);
            font-size: 15px;
            margin: 0;
            letter-spacing: 0.5px;
        '>Simply navigate to the section of your choice using the sidebar.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        @keyframes floatCard {
            0%   { transform: translateY(0px); }
            50%  { transform: translateY(-8px); }
            100% { transform: translateY(0px); }
        }
        @keyframes borderRotate {
            0%   { background-position: 0% 50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes shimmerFlow {
            0%   { left: -100%; }
            100% { left: 200%; }
        }
        @keyframes pulseIcon {
            0%   { transform: scale(1); }
            50%  { transform: scale(1.15); }
            100% { transform: scale(1); }
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        .how-card-wrapper {
            padding: 2px;
            border-radius: 16px;
            background: linear-gradient(270deg, #FF6B6B, #667eea, #11998e, #f7971e, #FF6B6B);
            background-size: 300% 300%;
            animation: borderRotate 4s ease infinite, floatCard 4s ease-in-out infinite;
            margin: 8px 0;
        }
        .how-card-inner {
            background: linear-gradient(135deg, #1a1d2e 0%, #1E2130 60%, #252840 100%);
            border-radius: 14px;
            padding: 24px 20px;
            min-height: 320px;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }
        .how-card-inner::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 40%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255,255,255,0.04),
                transparent
            );
            animation: shimmerFlow 3s ease-in-out infinite;
        }
        .how-card-title {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            font-size: 18px;
            font-weight: 700;
            color: white;
            margin-bottom: 12px;
            text-align: center;
        }
        .how-card-title img {
            animation: pulseIcon 3s ease-in-out infinite;
        }
        .how-card-desc {
            color: gray;
            text-align: center;
            font-size: 13px;
            margin-bottom: 8px;
        }
        .how-card-list {
            color: #8892a4;
            font-size: 12px;
            padding-left: 16px;
        }
        .how-card-list li {
            margin-bottom: 6px;
            line-height: 1.5;
        }
        .how-card-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
            margin: 12px 0;
        }
        .how-card-find {
            color: rgba(255,255,255,0.5);
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1px;
            text-align: center;
            margin-bottom: 8px;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class='how-card-wrapper' style='animation-delay: 0s;'>
            <div class='how-card-inner'>
                <div class='how-card-title'>
                    <img src='app/static/overview.png' width='30'/>
                    Overview
                </div>
                <p class='how-card-desc'>
                    Get a high-level summary of all products and sellers.
                </p>
                <div class='how-card-divider'></div>
                <p class='how-card-find'>WHAT YOU'LL FIND</p>
                <ul class='how-card-list'>
                    <li>Total listings, products and sellers</li>
                    <li>Listings by category</li>
                    <li>Top sellers by listings</li>
                    <li>Category summary table</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class='how-card-wrapper' style='animation-delay: 0.5s;'>
            <div class='how-card-inner'>
                <div class='how-card-title'>
                    <img src='app/static/price-analysis.png' width='30'/>
                    Price Analysis
                </div>
                <p class='how-card-desc'>
                    Dive deep into price trends and ranges across products.
                </p>
                <div class='how-card-divider'></div>
                <p class='how-card-find'>WHAT YOU'LL FIND</p>
                <ul class='how-card-list'>
                    <li>Average price over time per product</li>
                    <li>Price range box plots</li>
                    <li>Price statistics per product</li>
                    <li>Discounted products</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class='how-card-wrapper' style='animation-delay: 1s;'>
            <div class='how-card-inner'>
                <div class='how-card-title'>
                    <img src='app/static/seller-intelligence.png' width='30'/>
                    Seller Intelligence
                </div>
                <p class='how-card-desc'>
                    Analyze seller competition, ratings and more.
                </p>
                <div class='how-card-divider'></div>
                <p class='how-card-find'>WHAT YOU'LL FIND</p>
                <ul class='how-card-list'>
                    <li>Seller count per product</li>
                    <li>Cheapest seller per product</li>
                    <li>Average rating by seller</li>
                    <li>Rating status distribution</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Pipeline Section
st.markdown("""
    <style>
        @keyframes moveArrow {
            0%   { transform: translateX(0px); opacity: 0.3; }
            50%  { transform: translateX(8px); opacity: 1; }
            100% { transform: translateX(0px); opacity: 0.3; }
        }
        .animated-arrow {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            padding-top: 20px;
            animation: moveArrow 1.2s ease-in-out infinite;
            font-size: 28px;
            color: #FF6B6B;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
    ">
        <img src="app/static/data-pipeline.png" width="35" style="display: inline-block;">
        <h2 style="margin: 0;" class="section-title-main">DATA PIPELINE</h2>
    </div>
""", unsafe_allow_html=True)

col1, arr1, col2, arr2, col3, arr3, col4, arr4, col5 = st.columns([2,1,2,1,2,1,2,1,2])

with col1:
    st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <img src='app/static/serpapi-icon.png' width='50'/>
            <p style='color: gray; margin-top: 10px;'><b>SerpAPI</b><br>Google Shopping</p>
        </div>
    """, unsafe_allow_html=True)

with arr1:
    st.markdown("<div class='animated-arrow'>→</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <img src='app/static/dlt-icon.png' width='50'/>
            <p style='color: gray; margin-top: 10px;'><b>dlt</b><br>Data Loading</p>
        </div>
    """, unsafe_allow_html=True)

with arr2:
    st.markdown("<div class='animated-arrow'>→</div>", unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <img src='app/static/aws-s3-icon.png' width='50'/>
            <p style='color: gray; margin-top: 10px;'><b>AWS S3</b><br>Data Lake</p>
        </div>
    """, unsafe_allow_html=True)

with arr3:
    st.markdown("<div class='animated-arrow'>→</div>", unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <img src='app/static/amazon-rds-icon.png' width='50'/>
            <p style='color: gray; margin-top: 10px;'><b>AWS RDS</b><br>Data Warehouse</p>
        </div>
    """, unsafe_allow_html=True)

with arr4:
    st.markdown("<div class='animated-arrow'>→</div>", unsafe_allow_html=True)

with col5:
    st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <img src='app/static/dbt-icon.png' width='50'/>
            <p style='color: gray; margin-top: 10px;'><b>dbt</b><br>Transformations</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Copyright 
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 16px;'>© 2026 Retail Price Dashboard  </p>",
    unsafe_allow_html=True
)