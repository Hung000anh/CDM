# pages/04_🌡️_Heatmap.py
"""
heatmap.py
"""

import utils.path_setup  # noqa: F401
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
from data.queries import get_asset_types, get_symbols_by_asset_type
from data.queries.symbols import get_countries, get_symbols_by_country
from components.tables.economic_table import render_economic_table
from data.queries.prices import get_prices, get_latest_prices
from data.queries.symbols import get_timeframes_by_symbol
from collections import defaultdict
import pandas as pd

SUPPORT_URL = "https://omg10.com/4/10659204"
ECONOMIC_ASSET_TYPE = "Economy"

KNOWN_INDICATORS = [
    "GDP", "Real GDP YoY", "Government Budget", "Government Debt To GDP",
    "Interest Rate", "Inflation Rate YoY", "Unemployment Rate",
    "Industrial Production YoY", "Current Account To GDP", "Balance Of Trade",
]


def _on_select_all_changed(all_key: str, item_keys: list[str]):
    val = st.session_state[all_key]
    for k in item_keys:
        st.session_state[k] = val


def _on_item_changed(all_key: str, item_keys: list[str]):
    st.session_state[all_key] = all(st.session_state.get(k, True) for k in item_keys)


def render_heatmap_sidebar() -> dict | None:
    with st.sidebar:
        # ── Step 1: Market Type ─────────────────────────────────────────────
        asset_types = get_asset_types()
        if not asset_types:
            st.warning("No asset types found.")
            return None

        asset_type_names = [a["name"] for a in asset_types]
        selected_at_name = st.selectbox(
            "🏷️ Market Type",
            options=asset_type_names,
            key="heatmap_selectbox_asset_type",
        )
        selected_at   = next(a for a in asset_types if a["name"] == selected_at_name)
        asset_type_id = selected_at["id"]
        is_economic   = selected_at_name == ECONOMIC_ASSET_TYPE

        st.divider()

        # ── Step 2a (Economic): Select Country ──────────────────────────────
        if is_economic:
            countries = get_countries()
            if not countries:
                st.info("No countries found.")
                return None

            all_key   = "hm_chk_all_countries"
            item_keys = [f"hm_chk_country_{c['id']}" for c in countries]

            for k in item_keys:
                st.session_state.setdefault(k, True)
            st.session_state.setdefault(all_key, True)

            selected_countries: list[dict] = []
            with st.expander("🌍 Country", expanded=True):
                st.checkbox(
                    "Select all",
                    key=all_key,
                    on_change=_on_select_all_changed,
                    args=(all_key, item_keys),
                )
                for c, k in zip(countries, item_keys):
                    st.checkbox(
                        c["name"],
                        key=k,
                        on_change=_on_item_changed,
                        args=(all_key, item_keys),
                    )
                    if st.session_state[k]:
                        selected_countries.append(c)

            if not selected_countries:
                st.caption("⚠️ No country selected.")
                return None

            is_all = len(selected_countries) == len(countries)

            if is_all:
                chosen_symbols = get_symbols_by_asset_type(asset_type_id)
            else:
                seen_ids: set = set()
                chosen_symbols = []
                for c in selected_countries:
                    for sym in get_symbols_by_country(asset_type_id, c["id"]):
                        if sym["id"] not in seen_ids:
                            chosen_symbols.append(sym)
                            seen_ids.add(sym["id"])

            if not chosen_symbols:
                st.info("No indicators found for selected countries.")
                return None

            return {
                "asset_type_id":      asset_type_id,
                "asset_type_name":    selected_at_name,
                "is_economic":        True,
                "selected_countries": selected_countries,
                "is_all_countries":   is_all,
                "symbols":            chosen_symbols,
            }

        # ── Step 2b (Normal): Select Symbols ────────────────────────────────
        symbols = get_symbols_by_asset_type(asset_type_id)
        if not symbols:
            st.info(f"No symbols found in **{selected_at_name}**.")
            return None

        all_key   = f"hm_chk_all_sym_{asset_type_id}"
        item_keys = [f"hm_chk_sym_{sym['id']}" for sym in symbols]

        for k in item_keys:
            st.session_state.setdefault(k, True)
        st.session_state.setdefault(all_key, True)

        chosen_symbols: list[dict] = []
        with st.expander("📌 Symbol", expanded=True):
            st.checkbox(
                "Select all",
                key=all_key,
                on_change=_on_select_all_changed,
                args=(all_key, item_keys),
            )
            for sym, k in zip(symbols, item_keys):
                st.checkbox(
                    sym["symbol"],
                    key=k,
                    on_change=_on_item_changed,
                    args=(all_key, item_keys),
                )
                if st.session_state[k]:
                    chosen_symbols.append(sym)

        if not chosen_symbols:
            st.caption("⚠️ No symbol selected.")

        return {
            "asset_type_id":   asset_type_id,
            "asset_type_name": selected_at_name,
            "is_economic":     False,
            "symbols":         chosen_symbols,
        }


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CDM | Heatmap",
    page_icon="🌡️",
    layout="wide",
)

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
    .support-fab:hover {{ opacity: 0.88; transform: translateY(-2px); }}
    </style>
    <a class="support-fab" href="{SUPPORT_URL}" target="_blank">🙏 Click ads to Support Me</a>
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
            🌡️ Heatmap
        </h1>
        <p style="font-size:14px;color:#666;margin:0 0 24px 0;">
            Visual strength & correlation across markets
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

sidebar = render_heatmap_sidebar()

if not sidebar or not sidebar["symbols"]:
    st.markdown(
        """
        <div style="display:flex;justify-content:center;align-items:center;
        height:60vh;flex-direction:column;gap:16px">
            <h1>🌡️ Heatmap</h1>
            <p>Select a market type and at least 1 symbol in the sidebar.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ── Heatmap content ────────────────────────────────────────────────────────

if sidebar["is_economic"]:
    # Tạo Economic Indicators Summary
    selected_countries = sidebar.get("selected_countries", [])
    countries_list = get_countries()
    country_id_to_name = {c["id"]: c["name"] for c in countries_list}

    # Collect tất cả symbol_timeframe_id để query một lần
    stf_ids = []
    symbol_info = []
    for sym in sidebar["symbols"]:
        tf_list = get_timeframes_by_symbol(sym["id"])
        if not tf_list:
            continue
        tf = tf_list[0]
        stf_id = tf["symbol_timeframe_id"]
        stf_ids.append(stf_id)
        symbol_info.append({
            "stf_id": stf_id,
            "sym": sym,
            "tf_name": tf["name"]
        })

    # Query tất cả giá cùng lúc
    with st.spinner("Loading economic data..."):
        latest_prices_dict = get_latest_prices(stf_ids, num_prices=2)

    econ_records = []
    for info in symbol_info:
        stf_id = info["stf_id"]
        sym = info["sym"]

        prices = latest_prices_dict.get(stf_id, [])
        current = prices[0] if prices else None
        previous = prices[1] if len(prices) >= 2 else None
        cid = sym.get("country_id")
        country = country_id_to_name.get(cid, "Unknown") if cid else "Unknown"
        raw_name = sym["name"].strip()
        indicator = next(
            (ind for ind in sorted(KNOWN_INDICATORS, key=len, reverse=True)
             if raw_name.endswith(ind)),
            raw_name,
        )
        econ_records.append({
            "country": country,
            "indicator": indicator,
            "current_value": current,
            "previous_value": previous,
        })

    st.markdown("## 📊 Heatmap of key economic indicators")
    st.divider()
    render_economic_table(pd.DataFrame(econ_records), filter_country=None)
    st.divider()

else:
    st.info("✅ Sidebar ready. Awaiting heatmap requirements...")
    st.write("**Selected symbols:**", [s["symbol"] for s in sidebar["symbols"]])