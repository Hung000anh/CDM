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
        'font-family:\'DM Mono\',monospace;font-size:12px;"'
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
            + (f'<br><span style="font-size:10.5px;color:{color};">{change}</span>' if change else "")
        )
    else:
        inner = f'<span style="color:#e8e8e8;">{val}</span>'

    return (
        f'<td style="text-align:right;padding:10px 14px;'
        f'font-family:\'DM Mono\',monospace;font-size:12px;">'
        f'{inner}</td>'
    )


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

    # ── Header row ────────────────────────────────────────────────────────────
    th_style = (
        'style="text-align:right;padding:10px 14px;font-size:11px;'
        'font-weight:700;color:#555;letter-spacing:1px;'
        'text-transform:uppercase;white-space:nowrap;'
        'border-bottom:2px solid #2a2a2a;"'
    )
    header_cells = "".join(f"<th {th_style}>{c}</th>" for c in cols)

    # ── Data rows ─────────────────────────────────────────────────────────────
    rows_html = []
    for country, row in table.iterrows():
        flag  = _flag_html(str(country))
        cells = "".join(_cell_html(str(row.get(c, "—")), c) for c in cols)
        rows_html.append(
            f'<tr style="border-bottom:1px solid #1a1a1a;transition:background .15s;"'
            f' onmouseover="this.style.background=\'#1a1a1a\'"'
            f' onmouseout="this.style.background=\'transparent\'">'
            f'  <td style="padding:10px 16px;white-space:nowrap;">'
            f'    <div style="display:flex;align-items:center;gap:10px;">'
            f'      {flag}'
            f'      <span style="font-size:13px;font-weight:700;color:#e0e0e0;">{country}</span>'
            f'    </div>'
            f'  </td>'
            f'  {cells}'
            f'</tr>'
        )

    html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap');
    .econ-wrap {{ overflow-x: auto; border-radius: 12px; border: 1px solid #222; margin-top: 8px; }}
    .econ-tbl  {{ width: 100%; border-collapse: collapse; background: #111; }}
    .econ-tbl thead tr {{ background: #0d0d0d; }}
    </style>
    <div class="econ-wrap">
      <table class="econ-tbl">
        <thead>
          <tr>
            <th style="text-align:left;padding:10px 16px;font-size:11px;
                font-weight:700;color:#555;letter-spacing:1px;
                text-transform:uppercase;border-bottom:2px solid #2a2a2a;">
              Country
            </th>
            {header_cells}
          </tr>
        </thead>
        <tbody>{"".join(rows_html)}</tbody>
      </table>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)