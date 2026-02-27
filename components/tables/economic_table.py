"""
components/tables/economic_table.py
────────────────────────────────────
Render bảng Economic Indicators theo quốc gia dạng st.dataframe.
"""

import re
import pandas as pd
import streamlit as st


# Map theo tên country trong bảng countries của DB
COUNTRY_CURRENCY = {
    # Tên đầy đủ
    "European Union": "EUR",
    "United Kingdom": "GBP",
    "United States":  "USD",
    "Japan":          "JPY",
    "Canada":         "CAD",
    "Australia":      "AUD",
    "New Zealand":    "NZD",
    "Switzerland":    "CHF",
    # Tên viết tắt (fallback nếu DB dùng tên ngắn)
    "Euro":           "EUR",
    "British":        "GBP",
    "Japanese":       "JPY",
    "Canadian":       "CAD",
    "Australian":     "AUD",
    "Swiss":          "CHF",
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
    "GDP",
    "Real GDP YoY",
    "Government Budget",
    "Government Debt To GDP",
    "Interest Rate",
    "Inflation Rate YoY",
    "Unemployment Rate",
    "Current Account To GDP",
    "Industrial Production YoY",
    "Balance Of Trade",
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


def _extract_indicator(name: str) -> str:
    """
    Strip prefix quốc gia: 'AU GDP' → 'GDP'.
    Sort dài nhất trước để tránh 'Government Debt To GDP' match thành 'GDP'.
    """
    name = name.strip()
    for ind in sorted(KNOWN_INDICATORS, key=len, reverse=True):
        if name.endswith(ind):
            return ind
    return name


def _scale(df: pd.DataFrame) -> pd.DataFrame:
    """
    GDP: DB lưu raw (1752190000000) → chia 1e12 → T.
    BOT: DB lưu raw (3373000000)    → chia 1e9  → B.
    """
    df = df.copy()
    for col in ["current_value", "previous_value"]:
        df.loc[df["indicator"] == "GDP",             col] /= GDP_SCALE
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


def _highlight(val: str, col_name: str) -> str:
    match = re.search(r"\(([-+]?[0-9.]+)", str(val))
    if not match:
        return ""
    change = float(match.group(1))
    if col_name in INVERSE_COLS:
        color = "orangered" if change > 0 else ("springgreen" if change < 0 else "gold")
    else:
        color = "springgreen" if change > 0 else ("orangered" if change < 0 else "gold")
    return f"color: {color}; font-weight: bold"


def render_economic_table(df: pd.DataFrame, filter_country: str | None = None) -> None:
    """
    Render bảng Economic Indicators dùng st.dataframe với Styler.

    Args:
        df:             Output của get_economic_latest() hoặc df được build
                        từ chosen_symbols — cột: country, indicator,
                        current_value, previous_value
        filter_country: Nếu truyền vào tên quốc gia (không phải 'Tất cả')
                        thì chỉ hiển thị hàng của quốc gia đó.
    """
    if df is None or df.empty:
        st.caption("⚠️ Không có dữ liệu bảng Economic.")
        return

    # Filter theo quốc gia nếu cần
    if filter_country:
        df = df[df["country"] == filter_country]
        if df.empty:
            st.caption(f"⚠️ Không có dữ liệu cho **{filter_country}**.")
            return

    # # ── DEBUG ──────────────────────────────────────────────────────────────
    # print("[DEBUG] ALL rows BEFORE scale:")
    # print(df[["country", "indicator", "current_value", "previous_value"]].to_string())

    df = _scale(df)

    # print("[DEBUG] ALL rows AFTER scale:")
    # print(df[["country", "indicator", "current_value", "previous_value"]].to_string())
    # # ── END DEBUG ───────────────────────────────────────────────────────────
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

    # Rename INVERSE_COLS sau khi đã rename cột
    renamed_inverse = {RENAME_COLS.get(c, c) for c in INVERSE_COLS}

    styled = table.style.apply(
        lambda col: [
            _highlight(val, col.name) if col.name in renamed_inverse
            else _highlight(val, col.name)
            for val in col
        ],
        axis=0,
    )

    st.dataframe(styled, width=True)