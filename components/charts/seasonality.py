"""
components/charts/seasonality.py
──────────────────────────────────
Tính và vẽ biểu đồ xu hướng mùa vụ (Seasonality).
"""

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from pandas.tseries.offsets import MonthEnd

_RCPARAMS = {
    "axes.titlesize":    10,
    "font.size":         8,
    "axes.labelsize":    7,
    "figure.facecolor":  "#212121",
    "axes.facecolor":    "#212121",
    "savefig.facecolor": "#212121",
    "axes.edgecolor":    "#555555",
    "axes.labelcolor":   "#ffffff",
    "xtick.color":       "#ffffff",
    "ytick.color":       "#ffffff",
    "text.color":        "#ffffff",
    "axes.grid":         True,
    "grid.color":        "#3a3a3a",
    "grid.linestyle":    "--",
    "grid.linewidth":    0.6,
    "grid.alpha":        0.5,
}

_MONTH_LABELS = ['Jan','Feb','Mar','Apr','May','Jun',
                 'Jul','Aug','Sep','Oct','Nov','Dec','Jan']


def add_seasonality_averages(
    df: pd.DataFrame,
    date_col: str = "timestamp",
    value_col: str = "close",
    start_year: int = 2005,
    periods: list[int] = [20, 15, 10, 5, 2],
) -> pd.DataFrame:
    """
    Tính bảng trung bình mùa vụ từ dữ liệu giá tháng.

    Returns:
        pd.DataFrame: index = period label (e.g. "20y_avg"), columns = 1..12
    """
    df = df.copy()

    # Chuẩn hóa index thành datetime
    if date_col == "timestamp" and date_col not in df.columns:
        # df đã được set_index timestamp (từ _prepare_df)
        df[date_col] = df.index
    else:
        df[date_col] = pd.to_datetime(df[date_col], utc=True, errors="coerce")
        df[date_col] = df[date_col].dt.tz_localize(None)

    df = df.sort_values(date_col).reset_index(drop=True)

    # Lọc từ start_year, giữ thêm 2 dòng năm trước để tính continuity
    df_from  = df[df[date_col].dt.year >= start_year]
    df_prev  = df[df[date_col].dt.year == start_year - 1].tail(2)
    df_filt  = pd.concat([df_prev, df_from]).reset_index(drop=True)

    # % thay đổi kỳ
    df_filt["pct_change"] = df_filt[value_col].pct_change() * 100

    # Dịch thời gian sang cuối tháng kế tiếp
    df_filt["time_shifted"] = df_filt[date_col] + MonthEnd(1)
    df_filt["year"]  = df_filt["time_shifted"].dt.year
    df_filt["month"] = df_filt["time_shifted"].dt.month

    # Pivot table year × month
    pivot = (
        df_filt.pivot_table(
            index="year", columns="month",
            values="pct_change", aggfunc="first",
        )
        .sort_index()
    )
    if (start_year - 1) in pivot.index:
        pivot = pivot.drop(start_year - 1)

    # Tính trung bình nhiều giai đoạn
    last_year = pivot.index.max()
    result = {}
    for n in periods:
        start_p = last_year - n + 1
        df_p    = pivot[pivot.index >= start_p]
        result[f"{n}y"] = df_p.mean(numeric_only=True)

    avg_df = pd.DataFrame(result).T
    avg_df.index.name = "period"
    return avg_df


def render_seasonality(
    df_1m: pd.DataFrame,
    symbol: str = "",
    figsize: tuple = (14, 2.0),
) -> None:
    """
    Vẽ biểu đồ Seasonality từ dữ liệu giá tháng (1M).

    Args:
        df_1m:   DataFrame giá 1M từ get_prices() – có cột timestamp, close
        symbol:  Tên symbol
        figsize: Kích thước figure
    """
    if df_1m is None or df_1m.empty:
        st.caption(f"⚠️ Không có dữ liệu 1M để tính Seasonality cho **{symbol}**")
        return

    try:
        df_sa = add_seasonality_averages(df_1m)
    except Exception as e:
        st.caption(f"⚠️ Lỗi tính Seasonality: {e}")
        return

    if df_sa.empty:
        st.caption(f"⚠️ Không đủ dữ liệu Seasonality cho **{symbol}**")
        return

    months = np.arange(1, 14)   # 1..13 (nối tháng 1 cuối)

    with plt.rc_context(_RCPARAMS):
        fig, ax = plt.subplots(figsize=figsize)

        for period in df_sa.index:
            row    = df_sa.loc[period]
            values = [row.get(m, np.nan) for m in range(1, 13)]
            values_loop = values + [values[0]]   # nối Jan cuối
            ax.plot(months, values_loop, marker="o", markersize=2,
                    linewidth=1.2, label=period)

        ax.axhline(0, color="#888888", linewidth=0.6, linestyle="--")
        ax.set_title(f"Seasonality")
        ax.set_xlabel("Month")
        ax.set_ylabel("% Change")
        ax.set_xticks(months)
        ax.set_xticklabels(_MONTH_LABELS, fontsize=7)
        ax.legend(fontsize=7, facecolor="#212121", edgecolor="#555555",
                  labelcolor="#ffffff", ncol=len(df_sa.index))

    st.pyplot(fig)
    plt.close(fig)