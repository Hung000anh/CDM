"""
dashboard.py
"""

import utils.path_setup  # noqa: F401
import sys
from pathlib import Path
from collections import defaultdict

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import streamlit as st
from components.sidebar import render_sidebar
from components.charts.candlestick import render_candlestick, render_line
from components.charts.outlook_pie import render_outlook_pie
from components.charts.cot_chart import render_cot_chart, render_net_noncommercial
from components.charts.seasonality import render_seasonality
from components.tables.economic_table import render_economic_table
from data.queries.prices import get_prices
from data.queries.symbols import get_timeframes_by_symbol, get_countries
from data.queries.myfxbook import get_community_outlook
from data.queries.cftc import get_cot_data

KNOWN_INDICATORS = [
    "GDP", "Real GDP YoY", "Government Budget", "Government Debt To GDP",
    "Interest Rate", "Inflation Rate YoY", "Unemployment Rate",
    "Industrial Production YoY", "Current Account To GDP", "Balance Of Trade",
]

SUPPORT_URL = "https://omg10.com/4/10659204"

# ── Country name → flag image (flagcdn.com) ───────────────────────────────────
COUNTRY_FLAG_CODE = {
    "Australia":      "au",
    "Canada":         "ca",
    "Switzerland":    "ch",
    "Euro Zone":        "eu",
    "European Union":   "eu",
    "United Kingdom": "gb",
    "Japan":          "jp",
    "New Zealand":    "nz",
    "United States":  "us",
    "Germany":        "de",
    "France":         "fr",
    "Italy":          "it",
    "China":          "cn",
    "India":          "in",
    "Brazil":         "br",
    "Russia":         "ru",
    "South Korea":    "kr",
    "Spain":          "es",
    "Netherlands":    "nl",
    "Sweden":         "se",
    "Norway":         "no",
}

def country_flag_img(country_name: str, size: int = 28) -> str:
    code = COUNTRY_FLAG_CODE.get(country_name, "")
    if not code:
        return "🌍"
    url = f"https://flagcdn.com/w40/{code}.png"
    return (
        f'<img src="{url}" width="{size}" height="{size}" '
        f'style="border-radius:50%;object-fit:cover;vertical-align:middle;'
        f'border:1px solid rgba(255,255,255,0.12);margin-right:10px;'
        f'box-shadow:0 2px 6px rgba(0,0,0,0.3);" />'
    )

def country_header_html(label: str, count: int, level: str = "h2") -> str:
    """Render group header với flag tròn + tên + số symbol."""
    flag   = country_flag_img(label)
    fsizes = {"h2": "24px", "h3": "19px"}
    fsize  = fsizes.get(level, "20px")
    return (
        f'<div style="display:flex;align-items:center;padding:6px 0 4px 0;">'
        f'  {flag}'
        f'  <span style="font-family:\'Sora\',sans-serif;font-size:{fsize};'
        f'font-weight:800;color:#f0f0f0;">{label}</span>'
        f'  <span style="font-size:12px;color:#555;margin-left:10px;'
        f'font-weight:400;">{count} indicator{"s" if count != 1 else ""}</span>'
        f'</div>'
    )


st.set_page_config(
    page_title="CDM | Dashboard",
    page_icon="🫓",
    layout="wide",
)

# ── Support Us button ─────────────────────────────────────────────────────────
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
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div style="padding: 24px 0 8px 0;">
        <div style="font-size:11px;color:#f97316;font-weight:700;
                    letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">
            Market Intelligence
        </div>
        <h1 style="font-family:'Sora',sans-serif;font-size:38px;
                   font-weight:900;margin:0 0 6px 0;line-height:1.1;">
            📊 Dashboard
        </h1>
        <p style="font-size:14px;color:#666;margin:0 0 24px 0;">
            Multi-timeframe analysis — Candlestick, COT, Seasonality & Community Outlook
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

sidebar = render_sidebar()
if not sidebar or not sidebar["symbols"]:
    st.markdown(
        """
        <div style="display:flex;justify-content:center;align-items:center;
        height:60vh;flex-direction:column;gap:16px">
            <h1>🫓 CDM</h1>
            <p>Select a market type and at least 1 symbol in the sidebar.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

is_economic    = sidebar["is_economic"]
chosen_symbols = sidebar["symbols"]
chosen_tfs     = sidebar["timeframes"]

if not is_economic and not chosen_tfs:
    st.warning("No timeframe selected.")
    st.stop()

# ── Outlook ───────────────────────────────────────────────────────────────────
outlook_lookup: dict = {}
if not is_economic:
    try:
        with st.spinner("Loading Community Outlook…"):
            outlook_raw = get_community_outlook()
            outlook_lookup = {s["name"].upper(): s for s in outlook_raw}
    except Exception as exc:
        st.warning(f"⚠️ Could not load Community Outlook: {exc}")


def _find_outlook(symbol_str: str) -> dict | None:
    base = symbol_str.split(":")[-1]
    key  = base.upper().replace("/", "").replace("_", "").replace(".", "")
    for candidate in [key, key[:6]]:
        if candidate in outlook_lookup:
            return outlook_lookup[candidate]
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# ECONOMIC
# ═══════════════════════════════════════════════════════════════════════════════
if is_economic:
    ECON_COLS = 3

    selected_countries = sidebar.get("selected_countries", [])
    is_all             = sidebar.get("is_all_countries", True)

    countries_list     = get_countries()
    country_id_to_name = {c["id"]: c["name"] for c in countries_list}

    grouped: dict = defaultdict(list)
    for sym in chosen_symbols:
        cid   = sym.get("country_id")
        cname = country_id_to_name.get(cid, "Other") if cid else "Other"
        grouped[cname].append(sym)

    if is_all or len(selected_countries) > 1:
        groups = dict(sorted(grouped.items()))
    else:
        groups = dict(grouped)

    if is_all:
        # st.markdown("## 🌐 All")
        st.divider()
    elif len(selected_countries) > 1:
        names = ", ".join(c["name"] for c in selected_countries)
        st.markdown(f"## 🌍 {names}")
        st.divider()

    econ_records = []

    for group_label, syms in groups.items():
        # ── Group header với flag tròn ────────────────────────────────────────
        level = "h3" if (is_all or len(selected_countries) > 1) else "h2"
        st.markdown(
            country_header_html(group_label, len(syms), level=level),
            unsafe_allow_html=True,
        )
        st.divider()

        cols = None
        for idx, sym in enumerate(syms):
            tf_list = get_timeframes_by_symbol(sym["id"])
            if not tf_list:
                continue
            tf      = tf_list[0]
            stf_id  = tf["symbol_timeframe_id"]
            tf_name = tf["name"]

            col_idx = idx % ECON_COLS
            if col_idx == 0:
                cols = st.columns(ECON_COLS)

            with cols[col_idx]:
                with st.spinner(f"{sym['name']}"):
                    df = get_prices(stf_id, tf_name)
                    render_line(df, symbol=sym["name"], timeframe=tf_name)

            current  = float(df["close"].iloc[-1]) if not df.empty else None
            previous = float(df["close"].iloc[-2]) if len(df) >= 2 else None
            cid      = sym.get("country_id")
            country  = country_id_to_name.get(cid, "Unknown") if cid else "Unknown"
            raw_name = sym["name"].strip()
            indicator = next(
                (ind for ind in sorted(KNOWN_INDICATORS, key=len, reverse=True)
                 if raw_name.endswith(ind)),
                raw_name,
            )
            econ_records.append({
                "country":        country,
                "indicator":      indicator,
                "current_value":  current,
                "previous_value": previous,
            })

        st.divider()

    st.markdown("## 📊 Economic Indicators Summary")
    st.divider()
    render_economic_table(pd.DataFrame(econ_records), filter_country=None)
    st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# NORMAL
# ═══════════════════════════════════════════════════════════════════════════════
else:
    n_tf     = len(chosen_tfs)
    _fsize   = {1: (14, 5), 2: (10, 5), 3: (8, 4.8)}
    fig_size = _fsize.get(n_tf, (7, 4.5))

    for sym in chosen_symbols:
        tf_list = get_timeframes_by_symbol(sym["id"])
        tf_map  = {tf["name"]: tf for tf in tf_list}
        if not any(tf in tf_map for tf in chosen_tfs):
            continue

        st.markdown(f"#### {sym['symbol']}")

        df_cache: dict[str, object] = {}
        candle_cols = st.columns(n_tf)
        for col_idx, tf_name in enumerate(chosen_tfs):
            with candle_cols[col_idx]:
                if tf_name not in tf_map:
                    st.empty()
                    continue
                stf_id = tf_map[tf_name]["symbol_timeframe_id"]
                with st.spinner(f"{sym['symbol']} [{tf_name}]"):
                    df = get_prices(stf_id, tf_name)
                    df_cache[tf_name] = df
                    render_candlestick(df, symbol=sym["symbol"], timeframe=tf_name, figsize=fig_size)

        outlook = _find_outlook(sym["symbol"])
        cftc_id = sym.get("cftc_contract_id")
        has_outlook = outlook is not None
        has_cot     = cftc_id is not None
        has_1m      = "1M" in tf_map

        if has_outlook or has_cot or has_1m:
            df_cot = None
            if has_cot:
                with st.spinner(f"COT {sym['symbol']}…"):
                    df_cot = get_cot_data(cftc_id)

            df_1m = df_cache.get("1M")
            if df_1m is None and has_1m:
                df_1m = get_prices(tf_map["1M"]["symbol_timeframe_id"], "1M")

            has_cot_data = df_cot is not None and not df_cot.empty
            has_1m_data  = df_1m  is not None and not df_1m.empty
            has_left     = has_1m_data or has_cot_data

            if has_left and has_outlook:
                col_left, col_right = st.columns([4, 1])
            elif has_left:
                col_left, col_right = st.container(), None
            elif has_outlook:
                col_left, col_right = None, st.container()
            else:
                col_left = col_right = None

            if col_left is not None:
                with col_left:
                    if has_1m_data:
                        render_seasonality(df_1m, symbol=sym["symbol"], figsize=(18, 1.5))
                    if has_cot_data:
                        render_cot_chart(
                            df_cot,
                            symbol=sym["symbol"],
                            cftc_name=sym.get("cftc_name", ""),
                            lookback=52,
                            figsize=(18, 1.5),
                        )
                        render_net_noncommercial(
                            df_cot,
                            symbol=sym["symbol"],
                            cftc_name=sym.get("cftc_name", ""),
                            lookback=52,
                            figsize=(18, 1.5),
                        )
            if col_right is not None and has_outlook:
                with col_right:
                    st.markdown("<br>", unsafe_allow_html=True)
                    render_outlook_pie(
                        symbol_name=sym["symbol"],
                        long_pct=outlook["longPercentage"],
                        short_pct=outlook["shortPercentage"],
                        figsize=(3.0, 3.0),
                    )

        st.divider()

st.markdown(
    f"<center style='color:#555;padding:12px 0 24px 0;font-size:13px;'>"
    f"CDM © 2026 &nbsp;·&nbsp; Built with Streamlit &nbsp;·&nbsp; "
    f"<a href='{SUPPORT_URL}' style='color:#f97316;text-decoration:none;'>🙏 Click ads to Support Me</a>"
    f"</center>",
    unsafe_allow_html=True,
)