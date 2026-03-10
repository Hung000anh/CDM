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
GMAIL              = "hung000anh@gmail.com"
BMC_URL            = "https://buymeacoffee.com/hung000anh"


def _get_available_timeframes(symbols: list[dict]) -> set[str]:
    available = set()
    for sym in symbols:
        for tf in get_timeframes_by_symbol(sym["id"]):
            available.add(tf["name"])
    return available


def _on_select_all_changed(all_key: str, item_keys: list[str]):
    """Select All toggled → apply value to all items."""
    val = st.session_state[all_key]
    for k in item_keys:
        st.session_state[k] = val


def _on_item_changed(all_key: str, item_keys: list[str]):
    """Any item toggled → sync Select All to reflect actual state."""
    st.session_state[all_key] = all(st.session_state.get(k, True) for k in item_keys)


def _render_sidebar_footer():
    """Buy Me a Coffee button + contact info — rendered at the bottom of sidebar."""
    st.divider()
    bmc_col, kofi_col = st.columns(2)
    with bmc_col:
        st.markdown(
            f"""
            <a href="{BMC_URL}" target="_blank"
            style="display:block;text-align:center;
                    background:linear-gradient(135deg,#f97316,#ef4444);
                    color:#fff;font-weight:700;font-size:13px;
                    padding:11px 0;border-radius:20px;text-decoration:none;
                    box-shadow:0 4px 12px rgba(0,0,0,0.3);">
                ☕ Buy Me a Coffee
            </a>
            """,
            unsafe_allow_html=True,
        )
    with kofi_col:
        st.markdown(
            """
            <a href="https://ko-fi.com/hunganhnguyen" target="_blank"
            style="display:block;text-align:center;
                    background:linear-gradient(135deg,#29abe0,#1a8cbf);
                    color:#fff;font-weight:700;font-size:13px;
                    padding:11px 0;border-radius:20px;text-decoration:none;
                    box-shadow:0 4px 12px rgba(0,0,0,0.3);">
                🧡 Ko-fi
            </a>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        f"""
        <div style="margin-top:16px;padding:14px 16px;
                    background:#1a1a1a;border:1px solid #2a2a2a;
                    border-radius:12px;text-align:center;">
            <div style="font-size:11px;color:#666;
                        text-transform:uppercase;letter-spacing:1.5px;
                        margin-bottom:8px;">Contact</div>
            <a href="https://mail.google.com/mail/?view=cm&to={GMAIL}"
               style="display:inline-flex;align-items:center;gap:7px;
                      color:#f97316;font-size:13px;font-weight:600;
                      text-decoration:none;">
                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15"
                     viewBox="0 0 24 24" fill="none" stroke="currentColor"
                     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect width="20" height="16" x="2" y="4" rx="2"/>
                  <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
                </svg>
                {GMAIL}
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> dict | None:
    with st.sidebar:
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

            all_key   = "chk_all_countries"
            item_keys = [f"chk_country_{c['id']}" for c in countries]

            # Init defaults
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
                _render_sidebar_footer()
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
                _render_sidebar_footer()
                return None

            _render_sidebar_footer()

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
            _render_sidebar_footer()
            return None

        all_key   = f"chk_all_sym_{asset_type_id}"
        item_keys = [f"chk_sym_{sym['id']}" for sym in symbols]

        # Init defaults
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

        _render_sidebar_footer()

        return {
            "asset_type_id":   asset_type_id,
            "asset_type_name": selected_at_name,
            "is_economic":     False,
            "symbols":         chosen_symbols,
            "timeframes":      selected_tfs,
        }