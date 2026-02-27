"""
home.py
"""

import streamlit as st

st.set_page_config(
    page_title="CDM | Home",
    page_icon="🫓",
    layout="wide",
)
SUPPORT_URL = "https://byvn.net/Hblp"
st.markdown(
    f"""
    <style>
    .support-fab {{
        position: fixed;
        bottom: 60px;
        right: 24px;
        z-index: 99999;
        background: linear-gradient(135deg, #f97316, #ef4444);
        color: #ffffff !important;
        font-size: 15px;
        font-weight: 700;
        padding: 13px 28px;
        border-radius: 24px;
        text-decoration: none !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.45);
        transition: opacity .2s, transform .2s;
    }}
    .support-fab:hover {{
        opacity: 0.88;
        transform: translateY(-2px);
    }}
    </style>
    <a class="support-fab" href="{SUPPORT_URL}" target="_blank">☕ Support Us</a>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="padding:40px 0 10px 0">
        <h1 style="font-size:42px;margin-bottom:10px">🫓 CDM</h1>
        <p style="font-size:18px;max-width:800px">
        CDM is an integrated market analysis platform.
        It provides price charts, COT positioning data, seasonality statistics,
        and community sentiment in a unified interface.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

st.markdown("## Core Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.image("https://images.unsplash.com/photo-1642790106117-e829e14a795f", use_container_width=True)
    st.markdown("### Candlestick & Volume")
    st.markdown("Multi-timeframe charts with consistent dark styling.")

with col2:
    st.image("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3", use_container_width=True)
    st.markdown("### COT & Positioning")
    st.markdown("COT Index, extreme zones, and net positioning analysis.")

with col3:
    st.image("https://images.unsplash.com/photo-1559526324-593bc073d938", use_container_width=True)
    st.markdown("### Seasonality & Sentiment")
    st.markdown("Seasonality averages and community sentiment visualization.")