"""
components/charts/cot_chart.py
───────────────────────────────
Vẽ COT Index (line chart + highlight vùng cực đoan) theo style gốc.
"""

import matplotlib.pyplot as plt
import streamlit as st

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
    "grid.color":        "#212121",
    "grid.linestyle":    "--",
    "grid.linewidth":    0.6,
    "grid.alpha":        0.5,
}


def render_cot_chart(
    df,
    symbol: str = "",
    lookback: int = 52,
    figsize: tuple = (25, 3),
) -> None:
    """
    Vẽ COT Index line chart cho 3 nhóm, highlight vùng cực đoan.

    Args:
        df:       Output của get_cot_data() – đã có cột report_date,
                  cot_index_commercial, cot_index_large, cot_index_retail
        symbol:   Tên symbol (dùng cho tiêu đề)
        lookback: Số tuần gần nhất hiển thị
        figsize:  Kích thước figure
    """
    if df is None or df.empty:
        st.caption(f"⚠️ Không có dữ liệu COT cho **{symbol}**")
        return

    needed = ["report_date", "cot_index_commercial", "cot_index_large", "cot_index_retail"]
    if not all(c in df.columns for c in needed):
        st.caption(f"⚠️ Dữ liệu COT thiếu cột cho **{symbol}**")
        return

    df_plot = df.dropna(subset=["cot_index_commercial"]).tail(lookback).copy()
    if df_plot.empty:
        st.caption(f"⚠️ Không đủ dữ liệu COT cho **{symbol}**")
        return

    with plt.rc_context(_RCPARAMS):
        fig, ax = plt.subplots(figsize=figsize)

        # Vẽ 3 đường COT Index
        ax.plot(df_plot["report_date"], df_plot["cot_index_commercial"],
                label="Commercial",       color="green")
        ax.plot(df_plot["report_date"], df_plot["cot_index_large"],
                label="Large Speculators", color="red")
        ax.plot(df_plot["report_date"], df_plot["cot_index_retail"],
                label="Retail",            color="blue")

        # Ngưỡng 20 / 80
        ax.axhline(80, color="white", linestyle="-", alpha=0.5)
        ax.axhline(20, color="white", linestyle="-", alpha=0.5)

        # Highlight vùng cực đoan
        for i in range(len(df_plot) - 1):
            comm  = df_plot["cot_index_commercial"].iloc[i]
            retail = df_plot["cot_index_retail"].iloc[i]
            x0 = df_plot["report_date"].iloc[i]
            x1 = df_plot["report_date"].iloc[i + 1]
            if comm > 80 and retail < 20:
                ax.axvspan(x0, x1, color="green", alpha=0.1)
            elif comm < 20 and retail > 80:
                ax.axvspan(x0, x1, color="red", alpha=0.1)

        title = f"COT Index"
        ax.set_title(title)
        ax.set_xlabel("Date")
        ax.set_ylabel("COT Index (0-100)")
        ax.legend()

    st.pyplot(fig)
    plt.close(fig)


def render_net_noncommercial(
    df,
    symbol: str = "",
    lookback: int = 52,
    figsize: tuple = (25, 3),
) -> None:
    """
    Vẽ Non-Commercial Net Position (line chart + đường 0).

    Args:
        df:       Output của get_cot_data() – có cột report_date, net_noncommercial
        symbol:   Tên symbol (dùng cho tiêu đề)
        lookback: Số tuần gần nhất hiển thị
        figsize:  Kích thước figure
    """
    if df is None or df.empty or "net_noncommercial" not in df.columns:
        st.caption(f"⚠️ Không có dữ liệu Net Non-Commercial cho **{symbol}**")
        return

    df_plot = df.dropna(subset=["net_noncommercial"]).tail(lookback).copy()
    if df_plot.empty:
        st.caption(f"⚠️ Không đủ dữ liệu Net Non-Commercial cho **{symbol}**")
        return

    with plt.rc_context(_RCPARAMS):
        fig, ax = plt.subplots(figsize=figsize)

        ax.plot(
            df_plot["report_date"],
            df_plot["net_noncommercial"],
            color="#2196F3",
            linewidth=1.5,
        )

        # Fill trên/dưới 0
        ax.fill_between(
            df_plot["report_date"],
            df_plot["net_noncommercial"],
            0,
            where=df_plot["net_noncommercial"] >= 0,
            color="#26a69a",
            alpha=0.2,
        )
        ax.fill_between(
            df_plot["report_date"],
            df_plot["net_noncommercial"],
            0,
            where=df_plot["net_noncommercial"] < 0,
            color="#ef5350",
            alpha=0.2,
        )

        ax.axhline(0, color="white", linewidth=0.8, linestyle="--")

        title = f"Non-Commercial Net Position"
        ax.set_title(title)
        ax.set_ylabel("Contracts")
        ax.grid(True, linewidth=0.3)

    st.pyplot(fig)
    plt.close(fig)