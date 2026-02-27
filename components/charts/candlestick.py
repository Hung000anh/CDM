"""
components/charts/full_chart.py
────────────────────────────────
Biểu đồ nến đơn giản: Candlestick + Volume, custom X-ticks.
"""

import io
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import streamlit as st

from config import COLOR_BULL, COLOR_BEAR, COLOR_LINE, TIMEFRAME_DAYS

# ── Style ─────────────────────────────────────────────────────────────────────
_STYLE = mpf.make_mpf_style(
    marketcolors=mpf.make_marketcolors(
        up=COLOR_BULL, down=COLOR_BEAR,
        edge="inherit", wick="inherit",
        volume="in",
    ),
    rc={
        "axes.grid":         True,
        "axes.titlesize":    13,
        "font.size":         11,
        "axes.labelsize":    9,
        "figure.facecolor":  "#212121",
        "axes.facecolor":    "#212121",
        "savefig.facecolor": "#212121",
        "axes.edgecolor":    "#555555",
        "axes.labelcolor":   "#ffffff",
        "xtick.color":       "#ffffff",
        "ytick.color":       "#ffffff",
        "text.color":        "#ffffff",
        "grid.color":        "#3a3a3a",
        "grid.linestyle":    "--",
        "grid.linewidth":    0.6,
        "grid.alpha":        0.5,
    },
)


# ═════════════════════════════════════════════════════════════════════════════
# X-ticks
# ═════════════════════════════════════════════════════════════════════════════

def _add_xticks(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    df = df.copy()
    dates = df.index
    if pd.api.types.is_datetime64tz_dtype(dates):
        dates = dates.tz_convert(None)

    df["is_tick"] = 0

    if timeframe == "1D":
        months = sorted(set((d.year, d.month) for d in dates))
        for y, m in months:
            cands = [d for d in dates if d.year == y and d.month == m and d.day <= 10]
            if cands:
                df.loc[dates == min(cands), "is_tick"] = 1

    elif timeframe == "1W":
        quarters = sorted(set((d.year, pd.Timestamp(d).quarter) for d in dates))
        for y, q in quarters:
            q_weeks = [d for d in dates if d.year == y and pd.Timestamp(d).quarter == q]
            if q_weeks:
                cand = min(q_weeks)
                q_start = pd.Timestamp(year=y, month=3 * (q - 1) + 1, day=1)
                if hasattr(cand, "tzinfo") and cand.tzinfo:
                    cand = cand.tz_localize(None)
                if (cand - q_start).days <= 10:
                    df.loc[dates == cand, "is_tick"] = 1

    elif timeframe == "1M":
        for y in sorted(dates.year.unique()):
            year_dates = dates[dates.year == y]
            jan = year_dates[year_dates.month == 1]
            if not jan.empty:
                first_jan = jan.min()
                if first_jan.day > 15:
                    prev = dates[dates.year == y - 1]
                    tick = prev.max() if not prev.empty else first_jan
                else:
                    tick = first_jan
            else:
                prev = dates[dates.year == y - 1]
                tick = prev.max() if not prev.empty else year_dates.min()
            df.loc[dates == tick, "is_tick"] = 1

    return df


# ═════════════════════════════════════════════════════════════════════════════
# Prepare DataFrame
# ═════════════════════════════════════════════════════════════════════════════

def _prepare(df: pd.DataFrame, timeframe: str) -> pd.DataFrame | None:
    if df is None or df.empty:
        return None

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").set_index("timestamp")
    df.index = df.index.tz_localize(None)
    df.index.name = "Date"

    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    df = df.dropna(subset=["open", "high", "low", "close"])
    if df.empty:
        return None

    df = _add_xticks(df, timeframe)
    return df


# ═════════════════════════════════════════════════════════════════════════════
# Render
# ═════════════════════════════════════════════════════════════════════════════

def render_candlestick(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str,
    figsize: tuple = (10, 5),
) -> None:
    df_full = _prepare(df, timeframe)
    if df_full is None:
        st.warning(f"⚠️ No data for **{symbol}** [{timeframe}]")
        return

    n_days = TIMEFRAME_DAYS.get(timeframe, 365)
    cutoff = df_full.index.max() - pd.Timedelta(days=n_days)
    df_vs  = df_full[df_full.index >= cutoff]
    if df_vs.empty:
        df_vs = df_full

    has_vol = (
        "volume" in df_vs.columns
        and df_vs["volume"].notna().any()
        and df_vs["volume"].sum() > 0
    )

    fig, axlist = mpf.plot(
        df_vs,
        type="candle",
        style=_STYLE,
        volume=bool(has_vol),
        figsize=figsize,
        title=timeframe,
        datetime_format="%d/%m/%Y",
        returnfig=True,
        tight_layout=False,
        warn_too_much_data=len(df_vs) + 1,
    )

    ax_price = axlist[0]

    # Custom X-ticks
    tick_dates = df_vs.index[df_vs["is_tick"] == 1]
    if len(tick_dates) > 0:
        positions   = [df_vs.index.get_loc(d) for d in tick_dates if d in df_vs.index]
        tick_labels = [d.strftime("%d/%m/%Y") for d in tick_dates if d in df_vs.index]
        if positions:
            ax_price.set_xticks(positions)
            ax_price.set_xticklabels(tick_labels, rotation=45, ha="center", fontsize=7)

    ax_price.tick_params(axis="x", length=0)
    ax_price.tick_params(axis="y", length=0)
    fig.subplots_adjust(left=0.08, right=0.95, top=0.9, bottom=0.2, hspace=0.0)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="#212121")
    plt.close(fig)
    buf.seek(0)
    st.image(buf, use_container_width=True)


def render_line(
    df,
    symbol: str,
    timeframe: str,
    figsize: tuple = (12, 5),
) -> None:
    """Render line chart for Economic indicators."""
    if df is None or df.empty:
        st.warning(f"⚠️ No data for **{symbol}** [{timeframe}]")
        return

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").set_index("timestamp")
    df.index = df.index.tz_localize(None)
    df.index.name = "Date"

    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["close"])

    if df.empty:
        st.warning(f"⚠️ No data for **{symbol}** [{timeframe}]")
        return

    _rc = {
        "axes.grid":         True,
        "axes.titlesize":    17,
        "font.size":         10,
        "axes.labelsize":    9,
        "figure.facecolor":  "#212121",
        "axes.facecolor":    "#212121",
        "savefig.facecolor": "#212121",
        "axes.edgecolor":    "#555555",
        "axes.labelcolor":   "#ffffff",
        "xtick.color":       "#ffffff",
        "ytick.color":       "#ffffff",
        "text.color":        "#ffffff",
        "grid.color":        "#3a3a3a",
        "grid.linestyle":    "--",
        "grid.linewidth":    0.6,
        "grid.alpha":        0.5,
    }

    with plt.rc_context(_rc):
        fig, ax = plt.subplots(figsize=figsize, facecolor="#212121")
        ax.set_facecolor("#212121")
        ax.plot(df.index, df["close"], color=COLOR_LINE, linewidth=1.2)
        ax.set_title(f"{symbol} [{timeframe}]", color="#ffffff")
        ax.tick_params(axis="x", length=0, colors="#ffffff")
        ax.tick_params(axis="y", length=0, colors="#ffffff")

        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
        fig.autofmt_xdate(rotation=30, ha="center")
        fig.subplots_adjust(left=0.08, right=0.95, top=0.88, bottom=0.2)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#212121")
    plt.close(fig)
    buf.seek(0)
    st.image(buf, use_container_width=True)