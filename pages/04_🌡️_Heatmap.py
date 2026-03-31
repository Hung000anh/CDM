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
import pandas as pd
import plotly.graph_objects as go
from config import SUPPORTED_TIMEFRAMES, TIMEFRAME_LABELS

SUPPORT_URL = "https://omg10.com/4/10659204"
ECONOMIC_ASSET_TYPE = "Economy"

def _get_available_timeframes(symbols: list[dict]) -> set[str]:
    available = set()
    for sym in symbols:
        for tf in get_timeframes_by_symbol(sym["id"]):
            available.add(tf["name"])
    return available
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

        # ── Step 3: Timeframes ──────────────────────────────────────────────
        st.divider()
        available_tfs = _get_available_timeframes(chosen_symbols)
        tf_options = [tf for tf in SUPPORTED_TIMEFRAMES if tf in available_tfs]
        
        if not tf_options:
            st.caption("⚠️ No timeframes available.")
            selected_tfs = []
        else:
            selected_tf = st.selectbox(
                "⏱️ Timeframe",
                options=tf_options,
                format_func=lambda x: TIMEFRAME_LABELS.get(x, x),
                key="hm_tf_selectbox"
            )
            selected_tfs = [selected_tf]

        # ── Support & Contact (Synced with Dashboard) ───────────────────────
        GMAIL   = "hung000anh@gmail.com"
        BMC_URL = "https://buymeacoffee.com/hung000anh"
        
        st.sidebar.divider()
        bmc_col, kofi_col = st.sidebar.columns(2)
        with bmc_col:
            st.markdown(
                f"""
                <a href="{BMC_URL}" target="_blank"
                style="display:block;text-align:center;
                        background:linear-gradient(135deg,#f97316,#ef4444);
                        color:#fff;font-weight:700;font-size:12px;
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
                        color:#fff;font-weight:700;font-size:12px;
                        padding:11px 0;border-radius:20px;text-decoration:none;
                        box-shadow:0 4px 12px rgba(0,0,0,0.3);">
                    🧡 Ko-fi
                </a>
                """,
                unsafe_allow_html=True,
            )
        st.sidebar.markdown(
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

        return {
            "asset_type_id":   asset_type_id,
            "asset_type_name": selected_at_name,
            "is_economic":     False,
            "symbols":         chosen_symbols,
            "timeframes":      selected_tfs,
        }


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CDM | Heatmap",
    page_icon="🌡️",
    layout="wide",
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
    chosen_tfs = sidebar.get("timeframes", [])
    if not chosen_tfs:
        st.warning("No timeframes selected.")
        st.stop()

    st.markdown("## 📈 Performance Heatmap")
    st.divider()
    
    symbols = sidebar["symbols"]
    
    stf_ids = []
    symbol_tf_map = []
    
    for sym in symbols:
        tf_list = get_timeframes_by_symbol(sym["id"])
        tf_map = {tf["name"]: tf for tf in tf_list}
        for tf_name in chosen_tfs:
            if tf_name in tf_map:
                stf_id = tf_map[tf_name]["symbol_timeframe_id"]
                stf_ids.append(stf_id)
                symbol_tf_map.append({
                    "stf_id": stf_id,
                    "symbol": sym["symbol"],
                    "timeframe": tf_name
                })
                
    with st.spinner("Loading performance data..."):
        latest_prices_dict = get_latest_prices(stf_ids, num_prices=2)
        
    symbol_names = [s["symbol"] for s in symbols]
    df_heatmap = pd.DataFrame(index=symbol_names, columns=chosen_tfs, dtype=float)
    
    for info in symbol_tf_map:
        prices = latest_prices_dict.get(info["stf_id"], [])
        if len(prices) >= 2:
            current = prices[0]
            previous = prices[1]
            if previous and previous != 0:
                pct_change = (current - previous) / previous * 100
                df_heatmap.loc[info["symbol"], info["timeframe"]] = pct_change
        elif len(prices) == 1:
            df_heatmap.loc[info["symbol"], info["timeframe"]] = 0.0
            
    df_heatmap = df_heatmap.dropna(how='all').dropna(axis=1, how='all')
    
    if df_heatmap.empty:
        st.info("No data available to plot heatmap.")
    else:
        CURRENCY_TO_COUNTRY = {
            "AUD": "au", "CAD": "ca", "CHF": "ch", "EUR": "eu", "GBP": "gb",
            "JPY": "jp", "NZD": "nz", "USD": "us", "CNY": "cn", "HKD": "hk",
            "SGD": "sg", "MXN": "mx", "ZAR": "za", "TRY": "tr", "BRL": "br"
        }

        def get_pair_components(symbol_regex: str) -> tuple[str, str]:
            s = symbol_regex.upper()
            for sep in ["/", ":", "_", "-"]:
                if sep in s:
                    parts = s.split(sep)
                    return parts[0].strip(), parts[1].strip()
            if len(s) == 6:
                return s[:3], s[3:]
            # Fallback (Indices, Commodities often vs USD/index)
            if s.endswith("USDT"): return s[:-4], "USDT"
            if s.endswith("USD"): return s[:-3], "USD"
            return s, "USD"

        def get_flag_html(code: str, size: int = 24) -> str:
            c = code.upper()
            # Crypto Icons
            if c in ["BTC", "ETH", "USDT", "USDC", "BNB", "SOL", "XRP", "LTC", "ADA", "DOT"]:
                url = f"https://cryptoicons.org/api/icon/{c.lower()}/200"
                return f'<img src="{url}" width="{size}" height="{size}" style="vertical-align:middle;margin-right:8px;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.5));">'
            
            # Country Flags
            country_code = CURRENCY_TO_COUNTRY.get(c)
            if country_code:
                url = f"https://flagcdn.com/w40/{country_code}.png"
                return (
                    f'<img src="{url}" width="{size}" height="{size}" '
                    f'style="border-radius:50%;object-fit:cover;vertical-align:middle;'
                    f'margin-right:8px;border:1px solid rgba(255,255,255,0.1);'
                    f'box-shadow:0 2px 4px rgba(0,0,0,0.3);">'
                )
            return f'<span style="margin-right:8px;">🪙</span>'

        def get_currency_label(code: str) -> str:
            flag = get_flag_html(code)
            return f'<div style="display:flex;align-items:center;justify-content:center;">{flag} <b>{code}</b></div>'

        def generate_heatmap_html(df: pd.DataFrame) -> str:
            styles = """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=DM+Mono:wght@500&display=swap');
            .matrix-wrap {
                overflow-x: auto;
                border-radius: 16px;
                border: 1px solid #2a2e39;
                margin: 20px 0;
                box-shadow: 0 10px 40px rgba(0,0,0,0.5);
                background: #0b0e14;
            }
            .tv-heatmap {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                font-family: 'Sora', sans-serif;
                font-size: 13px;
                color: #d1d4dc;
            }
            .tv-heatmap th, .tv-heatmap td {
                border-right: 1px solid #1a1a1a;
                border-bottom: 1px solid #1a1a1a;
                text-align: center;
                vertical-align: middle;
                padding: 14px 10px;
                min-width: 100px;
                transition: all 0.2s ease;
            }
            .tv-heatmap th {
                background-color: #161a25;
                font-weight: 700;
                color: #848e9c;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-size: 11px;
                position: sticky;
                top: 0;
                z-index: 10;
            }
            .tv-heatmap-row-header {
                background-color: #161a25 !important;
                text-align: left !important;
                font-weight: 700;
                padding-left: 18px !important;
                color: #f0f3fa;
                position: sticky;
                left: 0;
                z-index: 9;
                min-width: 140px !important;
            }
            
            /* Animation cho hàng */
            .matrix-row {
                animation: rowIn 0.5s ease forwards;
                opacity: 0;
            }
            @keyframes rowIn {
                from { opacity: 0; transform: translateX(-10px); }
                to { opacity: 1; transform: translateX(0); }
            }

            /* HIỆU ỨNG TƯƠNG TÁC (Interaction) */
            
            /* Highlight hàng khi hover */
            .tv-heatmap tr:hover td {
                background: rgba(255,255,255,0.03);
            }
            
            /* Highlight cột (sử dụng :hover-col hack hoặc JS-like CSS) */
            /* Để làm highlight cột bằng CSS thuần, ta dùng pointer-events kết hợp td:hover::after */
            .tv-heatmap td:hover {
                background: rgba(255,255,255,0.1) !important;
                transform: scale(1.05);
                box-shadow: 0 0 15px rgba(255,255,255,0.1);
                z-index: 5;
                cursor: crosshair;
                color: #fff !important;
            }
            
            /* Hiệu ứng đường kẻ đối chiếu (Crosshair) */
            .tv-heatmap td:hover::before {
                content: '';
                position: absolute;
                background-color: rgba(255,255,255,0.05);
                left: 0;
                width: 100%;
                height: 100%;
                top: -5000px;
                bottom: -5000px;
                z-index: -1;
                pointer-events: none;
            }
            .tv-heatmap { overflow: hidden; }
            </style>
            """
            
            html = ['<div class="matrix-wrap">', '<table class="tv-heatmap">']
            
            html.append('<thead><tr>')
            html.append('<th></th>')
            for col in df.columns:
                html.append(f'<th>{col}</th>')
            html.append('</tr></thead>')
            
            html.append('<tbody>')
            max_val = df.abs().max().max() if not df.empty else 1
            if pd.isna(max_val) or max_val == 0: max_val = 1
                
            for i in range(len(df)):
                row_label = df.index[i]
                delay = i * 0.05
                html.append(f'<tr class="matrix-row" style="animation-delay: {delay}s;">')
                html.append(f'<td class="tv-heatmap-row-header">{row_label}</td>')
                
                for j in range(len(df.columns)):
                    if df.index[i] == df.columns[j]:
                        html.append('<td style="background-color: #0b0e14;"></td>')
                        continue

                    val = df.iloc[i, j]
                    if pd.isna(val):
                        html.append('<td style="background-color: #0b0e14;"></td>')
                        continue
                        
                    color_style = ""
                    text_val = ""
                    if val > 0:
                        intensity = min(1.0, max(0.4, val / max_val))
                        r, g, b = int(8 * intensity), int(153 * intensity), int(129 * intensity)
                        color_style = f"background-color: rgba({r},{g},{b}, 0.85); color: #fff; font-weight: 700;"
                        text_val = f"+{val:.2f}%"
                    elif val < 0:
                        intensity = min(1.0, max(0.4, abs(val) / max_val))
                        r, g, b = int(242 * intensity), int(54 * intensity), int(69 * intensity)
                        color_style = f"background-color: rgba({r},{g},{b}, 0.85); color: #fff; font-weight: 700;"
                        text_val = f"{val:.2f}%"
                    else:
                        color_style = "background-color: #1a1e2a;"
                        text_val = "0.00%"
                    
                    html.append(f'<td style="{color_style}; position: relative;">{text_val}</td>')
                        
                html.append('</tr>')
                
            html.append('</tbody></table></div>')
            return styles + "".join(html)

        # Since only one timeframe is selected, we just render it without tabs
        tf_name = chosen_tfs[0]
        st.markdown(f"### Timeframe: {tf_name}")
        
        if tf_name not in df_heatmap.columns:
            st.info(f"No data for {tf_name}.")
        else:
            df_tf = df_heatmap[tf_name].dropna()
            if df_tf.empty:
                st.info(f"No data for {tf_name}.")
            else:
                pair_data = {}
                currency_codes = set()
                
                for sym_name, pct in df_tf.items():
                    base, quote = get_pair_components(sym_name)
                    pair_data[(base, quote)] = pct
                    currency_codes.add(base)
                    currency_codes.add(quote)
                
                sorted_codes = sorted(list(currency_codes))
                display_labels = [get_currency_label(c) for c in sorted_codes]
                code_to_label = {c: get_currency_label(c) for c in sorted_codes}
                
                df_matrix = pd.DataFrame(index=display_labels, columns=display_labels, dtype=float)
                
                for i, base_code in enumerate(sorted_codes):
                    for j, quote_code in enumerate(sorted_codes):
                        if base_code == quote_code:
                            continue
                        
                        # Direct
                        if (base_code, quote_code) in pair_data:
                            df_matrix.iloc[i, j] = pair_data[(base_code, quote_code)]
                        # Inverse
                        elif (quote_code, base_code) in pair_data:
                            inv_pct = pair_data[(quote_code, base_code)]
                            # (1 / price_new) / (1 / price_old) - 1  => (price_old / price_new) - 1
                            # price_new = price_old * (1 + pct/100)
                            # Result = (1 / (1 + pct/100) - 1) * 100
                            df_matrix.iloc[i, j] = (1 / (1 + inv_pct / 100.0) - 1) * 100.0
                
                # Cleanup: remove rows/cols that are entirely empty
                df_matrix = df_matrix.dropna(how='all', axis=0).dropna(how='all', axis=1)
                
                is_crypto = "CRYPTO" in sidebar["asset_type_name"].upper()
                
                if is_crypto:
                    # Premium Crypto Grid with Centered Icons
                    grid_html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;800&display=swap');
.crypto-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 24px;
    justify-content: center;
    padding: 30px 0;
    font-family: 'Sora', sans-serif;
}
.crypto-card {
    background: linear-gradient(145deg, #1e222d, #131722);
    border: 1px solid #2a2e39;
    border-radius: 20px;
    width: 200px;
    min-height: 240px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 24px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    position: relative;
    overflow: hidden;
    text-decoration: none;
}
.crypto-card:hover {
    transform: translateY(-8px);
    border-color: #363a45;
    box-shadow: 0 12px 48px rgba(0,0,0,0.6);
}
.crypto-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 4px;
    opacity: 0.8;
}
.bullish-border::before { background: #089981; }
.bearish-border::before { background: #f23645; }

.crypto-icon-wrapper {
    width: 80px;
    height: 80px;
    background: rgba(255,255,255,0.03);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
}
.crypto-icon {
    width: 56px;
    height: 56px;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5));
}
.crypto-sym {
    color: #f0f3fa;
    font-weight: 800;
    font-size: 20px;
    margin-bottom: 12px;
    letter-spacing: 1px;
}
.crypto-pct {
    padding: 8px 18px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 15px;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
.bullish-text { background: rgba(8, 153, 129, 0.2); color: #089981; border: 1px solid rgba(8, 153, 129, 0.3); }
.bearish-text { background: rgba(242, 54, 69, 0.2); color: #f23645; border: 1px solid rgba(242, 54, 69, 0.3); }
</style>
<div class="crypto-grid">
"""
                    
                    for sym_name, pct in df_tf.items():
                        base = get_pair_components(sym_name)[0].upper()
                        icon_url = f"https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/{base.lower()}.png"
                        border_cls = "bullish-border" if pct >= 0 else "bearish-border"
                        text_cls = "bullish-text" if pct >= 0 else "bearish-text"
                        
                        grid_html += f"""
<div class="crypto-card {border_cls}">
    <div class="crypto-icon-wrapper">
        <img class="crypto-icon" src="{icon_url}" onerror="this.src='https://cdn-icons-png.flaticon.com/128/2585/2585274.png'">
    </div>
    <div class="crypto-sym">{base}</div>
    <div class="crypto-pct {text_cls}">{pct:+.2f}%</div>
</div>
"""
                    
                    grid_html += "</div>"
                    st.markdown(grid_html, unsafe_allow_html=True)
                else:
                    if df_matrix.empty:
                        st.info("No valid pair combinations found to display.")
                    else:
                        st.markdown(generate_heatmap_html(df_matrix), unsafe_allow_html=True)

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown(
    f"""
    <div style="text-align: center; color: #666; font-size: 14px; padding-bottom: 40px;">
        CDM © 2026  ·  Built with <b>Streamlit</b>  ·  
        <a href="{SUPPORT_URL}" target="_blank" style="color: #f97316; text-decoration: none; font-weight: 700;">
            🙏 Click ads to Support Me
        </a>
    </div>
    """,
    unsafe_allow_html=True
)