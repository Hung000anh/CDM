"""
components/tables/economic_table.py
────────────────────────────────────
Render bảng Economic Indicators theo quốc gia dạng HTML custom
với flag ảnh tròn từ flagcdn.com.
"""

import re
import pandas as pd
import streamlit as st


COUNTRY_CURRENCY = {
    "European Union": "EUR",
    "United Kingdom": "GBP",
    "United States":  "USD",
    "Japan":          "JPY",
    "Canada":         "CAD",
    "Australia":      "AUD",
    "New Zealand":    "NZD",
    "Switzerland":    "CHF",
    "Euro":           "EUR",
    "British":        "GBP",
    "Japanese":       "JPY",
    "Canadian":       "CAD",
    "Australian":     "AUD",
    "Swiss":          "CHF",
}

COUNTRY_FLAG_CODE = {
    "Australia":      "au",
    "Canada":         "ca",
    "Switzerland":    "ch",
    "European Union": "eu",
    "Euro Zone":      "eu",
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

GDP_SCALE = 1e12
BOT_SCALE = 1e9

POINT_CHANGE_COLS = [
    "Real GDP YoY",
    "Government Budget",
    "Government Debt To GDP",
    "Interest Rate",
    "Inflation Rate YoY",
    "Unemployment Rate",
    "Industrial Production YoY",
    "Current Account To GDP",
]

COLS_ORDER = [
    "Interest Rate",             # 1. Lãi suất – driver chính của tỷ giá
    "Inflation Rate YoY",        # 2. Lạm phát – quyết định hướng lãi suất
    "Real GDP YoY",              # 3. GDP tăng trưởng – sức mạnh kinh tế
    "Unemployment Rate",         # 4. Thất nghiệp – Fed/CB theo dõi sát
    "Industrial Production YoY", # 5. Sản xuất – leading indicator
    "Balance Of Trade",          # 6. Cán cân thương mại – cung/cầu ngoại tệ
    "Current Account To GDP",    # 7. Tài khoản vãng lai – dòng vốn dài hạn
    "Government Budget",         # 8. Ngân sách – rủi ro tài khóa
    "Government Debt To GDP",    # 9. Nợ công – rủi ro tín dụng
    "GDP",                       # 10. GDP tuyệt đối – tham khảo quy mô
]

RENAME_COLS = {
    "Real GDP YoY":              "GDP Growth",
    "Inflation Rate YoY":        "Inflation Rate",
    "Industrial Production YoY": "Industrial Production",
    "Government Budget":         "Gov Budget",
    "Government Debt To GDP":    "Gov Debt/GDP",
    "Current Account To GDP":    "Current Account/GDP",
}

INVERSE_COLS = {"Gov Debt/GDP"}

KNOWN_INDICATORS = [
    "GDP", "Real GDP YoY", "Government Budget", "Government Debt To GDP",
    "Interest Rate", "Inflation Rate YoY", "Unemployment Rate",
    "Industrial Production YoY", "Current Account To GDP", "Balance Of Trade",
]


def _scale(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["current_value", "previous_value"]:
        df.loc[df["indicator"] == "GDP",              col] /= GDP_SCALE
        df.loc[df["indicator"] == "Balance Of Trade", col] /= BOT_SCALE
    return df


def _format_display(row: pd.Series) -> str:
    indicator = row["indicator"]
    current   = row["current_value"]
    previous  = row["previous_value"]
    country   = row["country"]

    if current is None:
        return "—"

    if indicator == "GDP":
        if not previous:
            return f"{current:.2f}T"
        change = (current - previous) / abs(previous) * 100
        sign = "+" if change >= 0 else ""
        return f"{current:.2f}T ({sign}{change:.2f}%)"

    elif indicator == "Balance Of Trade":
        currency = COUNTRY_CURRENCY.get(country, "")
        if not previous:
            return f"{current:.2f}B {currency}".strip()
        change = (current - previous) / abs(previous) * 100
        sign = "+" if change >= 0 else ""
        return f"{current:.2f}B {currency} ({sign}{change:.2f}%)".strip()

    elif indicator in POINT_CHANGE_COLS:
        if previous is None:
            return f"{current:.2f}%"
        change = current - previous
        sign = "+" if change >= 0 else ""
        return f"{current:.2f}% ({sign}{change:.2f} pts)"

    else:
        return f"{current:.2f}"


def _change_color(val: str, col_name: str) -> str:
    match = re.search(r"\(([-+]?[0-9.]+)", str(val))
    if not match:
        return "#cccccc"
    change = float(match.group(1))
    if col_name in INVERSE_COLS:
        return "#ff4444" if change > 0 else ("#44dd88" if change < 0 else "#f0c040")
    else:
        return "#44dd88" if change > 0 else ("#ff4444" if change < 0 else "#f0c040")


def _flag_html(country: str) -> str:
    code = COUNTRY_FLAG_CODE.get(country, "")
    if not code:
        return '<span style="font-size:20px;">🌍</span>'
    url = f"https://flagcdn.com/w40/{code}.png"
    return (
        f'<img src="{url}" width="26" height="26" '
        f'style="border-radius:50%;object-fit:cover;vertical-align:middle;'
        f'border:1px solid rgba(255,255,255,0.15);'
        f'box-shadow:0 1px 4px rgba(0,0,0,0.4);flex-shrink:0;" />'
    )


def _cell_html(val: str, col_name: str) -> str:
    empty_style = (
        'style="text-align:right;padding:10px 14px;color:#333;'
        'font-family:\'DM Mono\',monospace;font-size:14px;"'
    )
    if not val or val == "—":
        return f'<td {empty_style}>—</td>'

    color = _change_color(val, col_name)
    match = re.match(r"^([^(]+)(\(.*\))?$", val.strip())
    if match:
        main   = match.group(1).strip()
        change = match.group(2) or ""
        inner  = (
            f'<span style="color:#e8e8e8;font-weight:600;">{main}</span>'
            + (f'<br><span style="font-size:12px;color:{color};">{change}</span>' if change else "")
        )
    else:
        inner = f'<span style="color:#e8e8e8;">{val}</span>'

    return (
        f'<td style="text-align:right;padding:10px 14px;'
        f'font-family:\'DM Mono\',monospace;font-size:14px;">'
        f'{inner}</td>'
    )


def _get_score(val_str: str, indicator: str, all_vals: list[float]) -> float:
    # Trích xuất số thực từ chuỗi hiển thị (ví dụ "5.20% (+0.10 pts)" -> 5.20)
    import re
    match = re.match(r"^([-+]?[0-9.]+)", str(val_str).strip())
    if not match: return 0.5
    try:
        val = float(match.group(1))
    except: return 0.5
    
    clean_all = []
    for v in all_vals:
        if pd.notna(v): clean_all.append(v)
    if not clean_all: return 0.5
    
    min_v, max_v = min(clean_all), max(clean_all)
    if max_v == min_v: return 0.5
    
    score = (val - min_v) / (max_v - min_v)
    
    # Một số chỉ số "càng cao càng xấu" (Nợ, Thất nghiệp, Lạm phát cao quá mức)
    inverse_indicators = ["Unemployment Rate", "Inflation Rate", "Gov Debt/GDP", "Inflation Rate YoY", "Government Debt To GDP"]
    if any(ind in indicator for ind in inverse_indicators):
        score = 1 - score
    return score

def render_economic_table(df: pd.DataFrame, filter_country: str | None = None) -> None:
    if df is None or df.empty:
        st.caption("⚠️ Không có dữ liệu bảng Economic.")
        return

    if filter_country:
        df = df[df["country"] == filter_country]
        if df.empty:
            st.caption(f"⚠️ Không có dữ liệu cho **{filter_country}**.")
            return

    df = _scale(df)
    
    # Chuẩn bị dữ liệu số để tính toán heatmap color
    num_df = df.pivot(index="country", columns="indicator", values="current_value")
    
    df["display_value"] = df.apply(_format_display, axis=1)
    table = df.pivot_table(
        index="country",
        columns="indicator",
        values="display_value",
        aggfunc="first",
    )
    
    ordered = [c for c in COLS_ORDER if c in table.columns]
    extra   = [c for c in table.columns if c not in COLS_ORDER]
    table   = table[ordered + extra]
    table   = table.rename(columns=RENAME_COLS)
    
    cols = list(table.columns)

    rows_html = []
    for country, row in table.iterrows():
        flag = _flag_html(str(country))
        cells = []
        for c_name in cols:
            val_str = str(row.get(c_name, "—"))
            
            # Tính toán màu nền Heatmap
            orig_col = next((k for k, v in RENAME_COLS.items() if v == c_name), c_name)
            col_data = num_df[orig_col].tolist() if orig_col in num_df.columns else []
            score = _get_score(val_str, orig_col, col_data)
            
            # Mix màu: Red (0) -> Yellow (0.5) -> Green (1)
            if score > 0.5:
                # Greenish
                intensity = (score - 0.5) * 2
                bg_color = f"rgba(8, 153, 129, {0.1 + 0.3 * intensity})"
                text_color = "#44dd88"
            else:
                # Redish
                intensity = (0.5 - score) * 2
                bg_color = f"rgba(242, 54, 69, {0.1 + 0.3 * intensity})"
                text_color = "#ff6666"
                
            if val_str == "—":
                bg_color = "transparent"
                text_color = "#444"

            cells.append(
                f'<td style="text-align:right;padding:12px 14px;background:{bg_color};'
                f'border:1px solid #1a1a1a;transition:all 0.3s;">'
                f'<div style="color:{text_color};font-family:\'DM Mono\',monospace;font-weight:600;font-size:14px;">'
                f'{val_str}</div></td>'
            )

        rows_html.append(
            f'<tr class="econ-row">'
            f'  <td style="padding:12px 16px;white-space:nowrap;background:#0d0d0d;border:1px solid #1a1a1a;">'
            f'    <div style="display:flex;align-items:center;gap:12px;">'
            f'      {flag}'
            f'      <span style="font-size:14px;font-weight:700;color:#f0f3fa;">{country}</span>'
            f'    </div>'
            f'  </td>'
            f'  {"".join(cells)}'
            f'</tr>'
        )

    th_style = (
        'style="text-align:right;padding:14px 18px;font-size:11px;'
        'font-weight:800;color:#848e9c;letter-spacing:1px;min-width:140px;'
        'text-transform:uppercase;border:1px solid #1a1a1a;background:#161a25;"'
    )
    header_cells = "".join(f"<th {th_style}>{c}</th>" for c in cols)

    html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;600&family=Sora:wght@400;700&display=swap');
    .econ-container {{
        overflow-x: auto;
        border-radius: 16px;
        border: 1px solid #2a2e39;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
        background: #0b0e14;
    }}
    .econ-tbl {{
        width: 100%;
        border-collapse: collapse;
        font-family: 'Sora', sans-serif;
    }}
    .econ-row {{
        transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), background 0.2s;
        animation: fadeIn 0.6s ease forwards;
        opacity: 0;
    }}
    .econ-row:hover {{
        background: rgba(255,255,255,0.07) !important;
        transform: scale(1.005);
        z-index: 10;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }}
    .econ-tbl td {{
        padding: 14px 18px;
        border: 1px solid #1a1a1a;
        min-width: 140px;
    }}
    .country-cell {{
        min-width: 220px !important;
        background: #0d0d0d !important;
        position: sticky;
        left: 0;
        z-index: 5;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(15px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .econ-row:nth-child(1) {{ animation-delay: 0.1s; }}
    .econ-row:nth-child(2) {{ animation-delay: 0.15s; }}
    .econ-row:nth-child(3) {{ animation-delay: 0.2s; }}
    .econ-row:nth-child(4) {{ animation-delay: 0.25s; }}
    .econ-row:nth-child(5) {{ animation-delay: 0.3s; }}
    </style>
    <div class="econ-container">
      <table class="econ-tbl">
        <thead>
          <tr>
            <th style="text-align:left;padding:14px 20px;font-size:11px;
                font-weight:800;color:#848e9c;letter-spacing:1px;min-width:220px;
                text-transform:uppercase;border:1px solid #1a1a1a;background:#161a25;
                position:sticky;left:0;z-index:6;">
              Market / Indicator
            </th>
            {header_cells}
          </tr>
        </thead>
        <tbody>{"".join(rows_html)}</tbody>
      </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)