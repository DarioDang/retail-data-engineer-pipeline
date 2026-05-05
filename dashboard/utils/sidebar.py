import streamlit as st
import os
import base64

# ── Get absolute path to static folder ────────────────────────────────────────
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")


def get_icon(filename):
    return os.path.join(STATIC_DIR, filename)

def get_icon(filename):
    return os.path.join(STATIC_DIR, filename)

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Load background once at module level
BG_PATH = os.path.join(os.path.dirname(__file__), "..", "image", "background", "background-1.jpg")
BG_BASE64 = get_base64_image(BG_PATH)

# Load portfolio icon
portfolio_icon_path = os.path.join(os.path.dirname(__file__), "static", "portfolio-sidebar-icon.png")
with open(portfolio_icon_path, "rb") as f:
    portfolio_icon_b64 = base64.b64encode(f.read()).decode()


def render_sidebar():
    st.markdown(f"""
        <style>
            [data-testid="stSidebarNav"] {{ display: none; }}

            /* ── Remove sidebar own background — use page background ── */
            [data-testid="stSidebar"] {{
                background: transparent !important;
                background-image: none !important;
            }}

            /* ── Remove sidebar content background ────────────────── */
            [data-testid="stSidebar"] > div:first-child {{
                background: transparent !important;
            }}

            [data-testid="stSidebarContent"] {{
                background: transparent !important;
            }}

            /* ── Nav link hover ───────────────────────────────────── */
            [data-testid="stSidebar"] a {{
                border-radius: 10px;
                padding: 10px 16px;
                margin: 4px 8px;
                transition: all 0.3s ease;
                border-left: 3px solid transparent;
            }}
            [data-testid="stSidebar"] a:hover {{
                background: rgba(255, 107, 107, 0.08);
                border-left: 3px solid #FF6B6B;
                transform: translateX(4px);
            }}
            [data-testid="stSidebar"] a[aria-current="page"] {{
                background: linear-gradient(90deg, rgba(255,107,107,0.15), transparent);
                border-left: 3px solid #FF6B6B;
                animation: sidebarGlow 2s ease-in-out infinite;
            }}
            [data-testid="stSidebar"] a span {{
                color: rgba(255,255,255,0.8) !important;
                font-size: 13px !important;
                font-weight: 600 !important;
                letter-spacing: 0.5px;
            }}
            [data-testid="stSidebar"] a[aria-current="page"] span {{
                color: #FF6B6B !important;
            }}
            @keyframes sidebarGlow {{
                0%   {{ box-shadow: -2px 0 8px rgba(255,107,107,0.2); }}
                50%  {{ box-shadow: -2px 0 16px rgba(255,107,107,0.5); }}
                100% {{ box-shadow: -2px 0 8px rgba(255,107,107,0.2); }}
            }}

            /* ── Fix icon + label alignment ───────────────────────── */
            [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
                gap: 0px !important;
            }}
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {{
                align-items: center !important;
                gap: 0px !important;
                margin: 2px 0 !important;
            }}
            [data-testid="stSidebar"] [data-testid="stImage"] {{
                display: flex;
                align-items: center;
                padding-top: 2px;
            }}
            [data-testid="stSidebar"] [data-testid="stPageLink"] {{
                display: flex;
                align-items: center;
                padding: 0 !important;
            }}
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Branding
        st.markdown("""
            <div style='padding: 12px 16px 10px 16px;
                        border-bottom: 1px solid rgba(255,255,255,0.12);
                        margin-bottom: 8px;'>
                <p style='color: #FF6B6B; font-size: 15px; font-weight: 800;
                          letter-spacing: 3px; margin: 0;'>
                    DASHBOARD CATEGORY
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Spacer to push nav items below the branding line
        st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)

        pages = [
            {"label": "Home",               "icon": get_icon("home-icon.png"),           "target": "Home.py"},
            {"label": "Overview",           "icon": get_icon("overview.png"),             "target": "pages/1_Overview.py"},
            {"label": "Price Analysis",     "icon": get_icon("price-analysis.png"),       "target": "pages/2_Price_Analysis.py"},
            {"label": "Seller Intelligence","icon": get_icon("seller-intelligence.png"),  "target": "pages/3_Seller_Intelligence.py"},
        ]

        for page in pages:
            col_icon, col_label = st.columns([1, 4], vertical_alignment="center")
            with col_icon:
                st.image(page["icon"], width=22)
            with col_label:
                st.page_link(page["target"], label=page["label"])
        
        # Profile Section
        st.markdown("""
            <style>
                .sidebar-footer {
                    position: fixed;
                    bottom: 0;
                    left: 0;
                    width: 240px;
                    padding: 16px;
                    border-top: 1px solid rgba(255,255,255,0.08);
                }
                .footer-profile-row {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    margin-bottom: 2px;
                }
                .footer-avatar {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #FF6B6B, #f7971e);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 11px;
                    font-weight: 800;
                    color: white;
                    flex-shrink: 0;
                }
                .footer-name {
                    color: white;
                    font-size: 13px;
                    font-weight: 700;
                    letter-spacing: 0.5px;
                    margin-bottom: 2px;
                }
                .footer-title {
                    color: rgba(255,255,255,0.4);
                    font-size: 10px;
                    font-weight: 300;
                    letter-spacing: 1px;
                    margin-bottom: 5px;
                    white-space: nowrap;
                }
                .footer-divider {
                    height: 1px;
                    background: linear-gradient(90deg, rgba(255,255,255,0.12), transparent);
                    margin: 8px 0;
                }
                .footer-links {
                    display: flex;
                    flex-direction: column;
                    gap: 0px;
                }
                .footer-link {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    text-decoration: none;
                    padding: 7px 4px;
                    border-radius: 0;
                    border: none;
                    border-bottom: 1px solid rgba(255,255,255,0.06);
                    background: transparent;
                }
                .footer-link:first-child {
                    border-top: 1px solid rgba(255,255,255,0.06);
                }
                .footer-link:hover {
                    background: transparent !important;
                    background-color: transparent !important;
                    border-color: rgba(255,255,255,0.06) !important;
                }
                .footer-link:focus,
                .footer-link:active,
                .footer-link:visited {
                    background: transparent !important;
                    background-color: transparent !important;
                    outline: none !important;
                }
                .footer-link-icon {
                    font-size: 14px;
                    width: 16px;
                    text-align: center;
                }
                .footer-link-text {
                    font-size: 11px;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                }
                .footer-link.github    .footer-link-text { color: #e6edf3; }
                .footer-link.linkedin  .footer-link-text { color: #60a5fa; }
                .footer-link.portfolio .footer-link-text { color: #FF6B6B; }
            </style>

            <div class='sidebar-footer'>
                <div class='footer-profile-row'>
                    <div class='footer-avatar'>DD</div>
                    <div>
                        <p class='footer-name'>Dario Dang</p>
                        <p class='footer-title'>Data Analyst</p>
                    </div>
                </div>
                <div class='footer-divider'></div>
                <div class='footer-links'>
                    <a class='footer-link github'
                    href='https://github.com/DarioDang'
                    target='_blank'>
                        <span class='footer-link-icon'>
                            <svg width='14' height='14' viewBox='0 0 24 24' fill='#e6edf3'>
                                <path d='M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z'/>
                            </svg>
                        </span>
                        <span class='footer-link-text'>GitHub</span>
                    </a>
                    <a class='footer-link linkedin'
                    href='https://www.linkedin.com/in/dario-dang-89049020a/'
                    target='_blank'>
                        <span class='footer-link-icon'>
                            <svg width='14' height='14' viewBox='0 0 24 24' fill='#60a5fa'>
                                <path d='M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z'/>
                            </svg>
                        </span>
                        <span class='footer-link-text'>LinkedIn</span>
                    </a>
                    <a class='footer-link portfolio'
                        href='https://dariodang.github.io/'
                        target='_blank'>
                        <img src='data:image/png;base64,{portfolio_icon_b64}' 
                            width='18' height='18'
                            style='vertical-align:middle; margin-right:0px;'/>
                        <span class='footer-link-text'>Portfolio</span>
                    </a>
                </div>
            </div>
        """, unsafe_allow_html=True)