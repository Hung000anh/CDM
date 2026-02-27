"""
components/sidebar.py
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
from data.queries import get_asset_types, get_symbols_by_asset_type, get_timeframes_by_symbol
from data.queries.symbols import get_countries, get_symbols_by_country
from config import SUPPORTED_TIMEFRAMES, TIMEFRAME_LABELS

ECONOMIC_ASSET_TYPE = "Economy"


def _get_available_timeframes(symbols: list[dict]) -> set[str]:
    available = set()
    for sym in symbols:
        for tf in get_timeframes_by_symbol(sym["id"]):
            available.add(tf["name"])
    return available


def render_sidebar() -> dict | None:
    with st.sidebar:
        # st.title("🫓 CDM")
        # st.divider()

        # ── Step 1: Asset Type ──────────────────────────────────────────────
        asset_types = get_asset_types()
        if not asset_types:
            st.warning("No asset types found.")
            return None

        asset_type_names = [a["name"] for a in asset_types]
        selected_at_name = st.selectbox(
            "🏷️ Market Type",
            options=asset_type_names,
            key="selectbox_asset_type",
        )
        selected_at   = next(a for a in asset_types if a["name"] == selected_at_name)
        asset_type_id = selected_at["id"]
        is_economic   = selected_at_name == ECONOMIC_ASSET_TYPE

        st.divider()

        # ── Step 2a (Economic): Select Country ─────────────────────────────
        if is_economic:
            countries = get_countries()
            if not countries:
                st.info("No countries found.")
                return None

            selected_countries: list[dict] = []
            with st.expander("🌍 Country", expanded=True):
                select_all_countries = st.checkbox("Select all", value=True, key="chk_all_countries")
                for c in countries:
                    if st.checkbox(c["name"], value=select_all_countries, key=f"chk_country_{c['id']}"):
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
                st.info("No economic indicators found for the selected countries.")
                return None

            return {
                "asset_type_id":      asset_type_id,
                "asset_type_name":    selected_at_name,
                "is_economic":        True,
                "selected_countries": selected_countries,
                "is_all_countries":   is_all,
                "symbols":            chosen_symbols,
                "timeframes":         [],
            }

        # ── Step 2b (Normal): Select Symbols ───────────────────────────────
        symbols = get_symbols_by_asset_type(asset_type_id)
        if not symbols:
            st.info(f"No symbols found in **{selected_at_name}**.")
            return None

        chosen_symbols: list[dict] = []
        with st.expander("📌 Symbol", expanded=True):
            select_all = st.checkbox("Select all", value=True, key=f"chk_all_sym_{asset_type_id}")
            for sym in symbols:
                label = sym["symbol"]
                if sym.get("exchange"):
                    # label += f" `{sym['exchange']}`"
                    label += f""
                if st.checkbox(label, value=select_all, key=f"chk_sym_{sym['id']}"):
                    chosen_symbols.append(sym)

        if not chosen_symbols:
            st.caption("⚠️ No symbol selected.")

        # ── Step 3: Timeframes ──────────────────────────────────────────────
        selected_tfs: list[str] = []
        st.divider()
        with st.expander("⏱️ Timeframe", expanded=True):
            available_tfs = _get_available_timeframes(symbols)
            for tf_name in SUPPORTED_TIMEFRAMES:
                label    = TIMEFRAME_LABELS.get(tf_name, tf_name)
                has_data = tf_name in available_tfs
                if has_data:
                    if st.checkbox(label, value=True, key=f"tf_chk_{tf_name}"):
                        selected_tfs.append(tf_name)
                else:
                    st.caption(f"~~{label}~~ _(no data)_")

        if not selected_tfs:
            st.caption("⚠️ No timeframe selected.")

        return {
            "asset_type_id":   asset_type_id,
            "asset_type_name": selected_at_name,
            "is_economic":     False,
            "symbols":         chosen_symbols,
            "timeframes":      selected_tfs,
        }