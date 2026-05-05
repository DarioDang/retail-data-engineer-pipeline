import streamlit as st

def hide_streamlit_ui():
    """Hide Streamlit default header, toolbar and footer."""
    st.markdown("""
        <style>
            header[data-testid="stHeader"] {
                background: transparent !important;
                backdrop-filter: none !important;
            }
            [data-testid="stToolbar"] {
                display: none !important;
            }
            footer {
                visibility: hidden !important;
            }
            .main .block-container {
                padding-top: 2rem !important;
            }
            [data-testid="stBottomBlockContainer"] {{
                display: none !important;
            }}

            [data-testid="stDecoration"] {{
                display: none !important;
            }}

            button[kind="managedApp"] {{
                display: none !important;
            }}
        </style>
    """, unsafe_allow_html=True)