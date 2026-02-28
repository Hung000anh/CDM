"""
00_🏠_Home.py
"""

import streamlit as st

st.set_page_config(
    page_title="CDM | Home",
    page_icon="🫓",
    layout="wide",
)

SUPPORT_URL = "https://byvn.net/Hblp"
BMC_URL     = "https://buymeacoffee.com/hung000anh"

# ── Global styles + Support FAB ───────────────────────────────────────────────
st.markdown(
    f"""
    <style>
    .block-container {{ padding-top: 2rem; }}

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
    .support-fab:hover {{ opacity: 0.88; transform: translateY(-2px); }}

    .metric-card {{
        background: #1e1e1e;
        border: 1px solid #2e2e2e;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }}
    .metric-card .metric-value {{
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.1;
    }}
    .metric-card .metric-label {{
        font-size: 13px;
        color: #888;
        margin-top: 4px;
    }}

    .feature-card {{
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 14px;
        padding: 28px 24px;
        height: 100%;
    }}
    .feature-card .icon {{ font-size: 32px; margin-bottom: 12px; }}
    .feature-card h3 {{ font-size: 18px; font-weight: 700; margin: 0 0 10px 0; color: #fff; }}
    .feature-card p  {{ font-size: 14px; color: #aaa; line-height: 1.6; margin: 0; }}

    .asset-row {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }}
    .asset-badge {{
        background: #2a2a2a;
        border: 1px solid #3a3a3a;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 12px;
        color: #bbb;
    }}

    .step-row {{ display: flex; align-items: flex-start; gap: 16px; margin-bottom: 24px; }}
    .step-num {{
        min-width: 36px; height: 36px;
        background: linear-gradient(135deg, #f97316, #ef4444);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 15px; color: #fff;
        flex-shrink: 0;
    }}
    .step-body h4 {{ margin: 0 0 4px 0; font-size: 15px; color: #fff; font-weight: 600; }}
    .step-body p  {{ margin: 0; font-size: 13px; color: #999; line-height: 1.6; }}

    .roadmap-card {{
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 14px;
        padding: 24px;
        height: 100%;
    }}
    .roadmap-card h4 {{
        font-size: 15px;
        font-weight: 700;
        color: #fff;
        margin: 0 0 6px 0;
    }}
    .roadmap-card p {{
        font-size: 13px;
        color: #888;
        margin: 0;
        line-height: 1.5;
    }}
    .roadmap-icon {{
        font-size: 22px;
        margin-bottom: 10px;
    }}
    .coming-soon-tag {{
        display: inline-block;
        background: rgba(249,115,22,0.12);
        border: 1px dashed #f97316;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 11px;
        color: #f97316;
        font-weight: 600;
        margin-bottom: 12px;
    }}

    .source-card {{
        background: #161616;
        border: 1px solid #2a2a2a;
        border-radius: 14px;
        padding: 24px 20px;
        text-align: center;
        height: 100%;
        transition: border-color .2s;
    }}
    .source-card:hover {{ border-color: #f97316; }}
    .source-card .src-icon {{ font-size: 36px; margin-bottom: 10px; }}
    .source-card h4 {{
        font-size: 15px; font-weight: 700;
        color: #fff; margin: 0 0 8px 0;
    }}
    .source-card p {{
        font-size: 12.5px; color: #888;
        line-height: 1.6; margin: 0;
    }}

    .disclaimer-box {{
        background: rgba(239,68,68,0.06);
        border: 1px solid rgba(239,68,68,0.25);
        border-left: 4px solid #ef4444;
        border-radius: 12px;
        padding: 24px 28px;
        margin-top: 8px;
    }}
    .disclaimer-box h4 {{
        color: #ef4444;
        font-size: 15px;
        font-weight: 700;
        margin: 0 0 12px 0;
    }}
    .disclaimer-box p {{
        color: #aaa;
        font-size: 13px;
        line-height: 1.8;
        margin: 0;
    }}
    .disclaimer-box strong {{ color: #ddd; }}
    </style>
    <a class="support-fab" href="{SUPPORT_URL}" target="_blank">🙏 Click to Support Us</a>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════════════
st.markdown(
    f"""
    <div style="padding: 48px 0 32px 0;">
        <div style="font-size:12px;color:#f97316;font-weight:700;
                    letter-spacing:3px;text-transform:uppercase;margin-bottom:14px;">
            Market Intelligence Platform
        </div>
        <div style="display:flex;align-items:center;gap:20px;margin:0 0 18px 0;flex-wrap:wrap;">
            <h1 style="font-size:52px;font-weight:900;margin:0;line-height:1.05;">
                🫓 CDM
            </h1>
            <a href="{BMC_URL}" target="_blank"
               style="display:inline-block;
                      background:linear-gradient(135deg,#f97316,#ef4444);
                      color:#fff;font-weight:700;font-size:14px;
                      padding:10px 22px;border-radius:20px;text-decoration:none;
                      box-shadow:0 4px 12px rgba(239,68,68,0.35);
                      white-space:nowrap;">
                ☕ Buy Me a Coffee
            </a>
        </div>
        <p style="font-size:17px;color:#999;max-width:600px;line-height:1.8;margin:0 0 36px 0;">
            An integrated platform combining price charts, COT positioning,
            seasonality statistics, and community sentiment — all in one place.
        </p>
        <a href="/Dashboard" target="_self"
           style="display:inline-block;
                  background:linear-gradient(135deg,#f97316,#ef4444);
                  color:#fff;font-weight:700;font-size:15px;
                  padding:14px 32px;border-radius:24px;text-decoration:none;
                  box-shadow:0 4px 14px rgba(239,68,68,0.35);">
            Open Dashboard →
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Stats ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
for col, (val, label) in zip(
    [c1, c2, c3, c4],
    [("3", "Asset Classes"), ("5", "Timeframes"), ("100+", "Symbols"), ("4h", "Sentiment Refresh")],
):
    with col:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{val}</div>'
            f'<div class="metric-label">{label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.divider()


# ═══════════════════════════════════════════════════════════════════
# CORE FEATURES
# ═══════════════════════════════════════════════════════════════════
st.markdown("## Core Features")
st.markdown("<br>", unsafe_allow_html=True)

for col, (icon, title, desc) in zip(
    st.columns(4),
    [
        ("📈", "Candlestick & Volume",
         "Multi-timeframe OHLCV charts with dark styling, swing high/low markers, "
         "and moving averages across 1D, 1W, and 1M."),
        ("📋", "COT Positioning",
         "COT Index (0–100) for Commercials, Large Speculators, and Retail. "
         "Highlights extreme zones and net non-commercial positions."),
        ("🌊", "Seasonality",
         "Monthly average % change over 2y, 5y, 10y, 15y, and 20y lookback periods. "
         "Identifies recurring seasonal patterns per symbol."),
        ("🧭", "Community Sentiment",
         "Long/Short % from Myfxbook community outlook, refreshed every 4 hours. "
         "Displayed as a donut chart alongside each symbol."),
    ],
):
    with col:
        st.markdown(
            f'<div class="feature-card">'
            f'<div class="icon">{icon}</div>'
            f'<h3>{title}</h3>'
            f'<p>{desc}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.divider()


# ═══════════════════════════════════════════════════════════════════
# DATA COVERAGE
# ═══════════════════════════════════════════════════════════════════
st.markdown("## Data Coverage")
st.markdown("<br>", unsafe_allow_html=True)

for col, (icon, title, desc, badges) in zip(
    st.columns(3),
    [
        (
            "🌍", "Forex",
            "Major and minor currency pairs with full OHLCV history, COT futures "
            "positioning, multi-timeframe structure, and real-time sentiment.",
            ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF", "..."],
        ),
        (
            "📊", "Economic",
            "Macro indicators across G8 economies — inflation, interest rates, "
            "GDP, unemployment, trade balance, and industrial production.",
            ["Interest Rate", "Inflation", "GDP", "Unemployment", "Gov Budget", "..."],
        ),
        (
            "₿", "Crypto",
            "Major digital assets with spot price, volume, COT futures positioning "
            "(where available), market structure, and community sentiment.",
            ["BTC", "ETH", "XRP"],
        ),
    ],
):
    badges_html = "".join(f'<span class="asset-badge">{b}</span>' for b in badges)
    with col:
        st.markdown(
            f'<div class="feature-card">'
            f'<div class="icon">{icon}</div>'
            f'<h3>{title}</h3>'
            f'<p>{desc}</p>'
            f'<div class="asset-row">{badges_html}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.divider()


# ═══════════════════════════════════════════════════════════════════
# ROADMAP
# ═══════════════════════════════════════════════════════════════════
st.markdown("## 🗺️ Roadmap")
st.markdown(
    "<p style='color:#888;font-size:14px;margin-bottom:24px;'>"
    "What we're researching and building next."
    "</p>",
    unsafe_allow_html=True,
)

roadmap_items = [
    ("₿", "Crypto Expansion",
     "Market cap, FDV, circulating/max/total supply, ATH tracking, and more pairs."),
    ("📈", "Stock Coverage",
     "Add symbols for stocks like SP500, E-mini S&P 500 (ES), Nasdaq 100 (NQ), Dow Jones (DJI)."),
]

cols = st.columns(4)
for i, (icon, title, desc) in enumerate(roadmap_items):
    with cols[i]:
        st.markdown(
            f'<div class="roadmap-card">'
            f'<div class="roadmap-icon">{icon}</div>'
            f'<div class="coming-soon-tag">Researching</div>'
            f'<h4>{title}</h4>'
            f'<p>{desc}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.divider()


# ═══════════════════════════════════════════════════════════════════
# HOW TO USE
# ═══════════════════════════════════════════════════════════════════
st.markdown("## How to Use")
st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns(2)
steps = [
    ("1", "Select a Market Type",
     "Open the sidebar and choose Forex, Economic, or Crypto from the asset type selector."),
    ("2", "Pick Your Symbols",
     "Select one or more symbols to analyze. For Economic, you can filter by country."),
    ("3", "Choose Timeframes",
     "Select the timeframes you want: 1D, 1W, 1M, 3M, or 12M."),
    ("4", "Analyze",
     "Charts, COT data, seasonality, and sentiment load automatically on the Dashboard."),
]

for col, (num, title, desc) in zip([left, left, right, right], steps):
    with col:
        st.markdown(
            f'<div class="step-row">'
            f'<div class="step-num">{num}</div>'
            f'<div class="step-body"><h4>{title}</h4><p>{desc}</p></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.divider()


# ═══════════════════════════════════════════════════════════════════
# DATA SOURCES
# ═══════════════════════════════════════════════════════════════════
st.markdown("## 📡 Data Sources")
st.markdown(
    "<p style='color:#888;font-size:14px;margin-bottom:24px;'>"
    "Data is collected and aggregated from the following publicly available sources."
    "</p>",
    unsafe_allow_html=True,
)

src_cols = st.columns(4)
sources = [
    (
        "📊", "TradingView",
        "Historical OHLCV price data for Forex, Crypto, and other financial assets. "
        "Primary source for candlestick charts and technical analysis.",
    ),
    (
        "🌐", "Myfxbook",
        "Community market sentiment data (Community Outlook) — real-time Long/Short "
        "ratios from retail traders, refreshed every 4 hours.",
    ),
    (
        "🏛️", "CFTC",
        "Weekly Commitment of Traders (COT) reports from the U.S. Commodity Futures "
        "Trading Commission. Basis for Large Speculator & Commercial positioning analysis.",
    ),
    (
        "🪙", "CoinGecko",
        "Cryptocurrency market data including price, market cap, trading volume, "
        "and general coin overview information.",
    ),
]

for col, (icon, name, desc) in zip(src_cols, sources):
    with col:
        st.markdown(
            f'<div class="source-card">'
            f'<div class="src-icon">{icon}</div>'
            f'<h4>{name}</h4>'
            f'<p>{desc}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.divider()


# ═══════════════════════════════════════════════════════════════════
# DISCLAIMER
# ═══════════════════════════════════════════════════════════════════
st.markdown("## ⚠️ Disclaimer")
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="disclaimer-box">
        <h4>⚠️ DISCLAIMER</h4>
        <p>
            All data, charts, and information displayed on this platform are
            <strong>intended solely for educational, research, and community reference purposes</strong>.
            I am <strong>not</strong> a financial advisor, do not provide investment
            recommendations, and bear no responsibility for any trading decisions made based
            on information from this platform.
        </p>
        <br>
        <p>
            Data is currently collected from publicly available sources including — but not
            limited to — <strong>TradingView, Myfxbook, CFTC, and CoinGecko</strong>.
            Additional sources may be integrated in the future as the platform expands.
            All data may be subject to delays, inaccuracies, or incompleteness. I make no
            guarantees regarding the accuracy, timeliness, or completeness of any
            information provided.
        </p>
        <br>
        <p>
            <strong>Financial trading involves substantial risk of loss.</strong> You may lose
            all of your invested capital. Always conduct your own research
            (<em>DYOR — Do Your Own Research</em>) and consult a qualified financial
            professional before making any investment decisions.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════
st.divider()
st.markdown(
    f"<center style='color:#555;padding:12px 0 24px 0;font-size:13px;'>"
    f"CDM © 2026 &nbsp;·&nbsp; Built with Streamlit &nbsp;·&nbsp; "
    f"<a href='{SUPPORT_URL}' style='color:#f97316;text-decoration:none;'>🙏 Click to Support Us</a>"
    f"</center>",
    unsafe_allow_html=True,
)