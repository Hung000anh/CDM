"""
components/charts/outlook_pie.py
─────────────────────────────────
Vẽ biểu đồ tròn Long / Short (Myfxbook Community Outlook).
Render dưới dạng ảnh PNG (nhất quán với candlestick).
"""

import io
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import streamlit as st


_BG       = "#212121"
_LONG_C   = "#26a69a"   # xanh lá – khớp COLOR_BULL
_SHORT_C  = "#ef5350"   # đỏ      – khớp COLOR_BEAR
_TEXT_C   = "#ffffff"


def render_outlook_pie(
    symbol_name: str,
    long_pct: float,
    short_pct: float,
    figsize: tuple = (3.2, 3.2),
) -> None:
    """
    Vẽ 1 pie chart cho 1 symbol.

    Args:
        symbol_name: Tên symbol (VD: "EURUSD")
        long_pct:    % Long (0-100)
        short_pct:   % Short (0-100)
        figsize:     Kích thước figure matplotlib
    """
    fig, ax = plt.subplots(figsize=figsize, facecolor=_BG)
    ax.set_facecolor(_BG)

    sizes  = [long_pct, short_pct]
    colors = [_LONG_C, _SHORT_C]
    labels = [f"Long\n{long_pct:.1f}%", f"Short\n{short_pct:.1f}%"]

    wedges, texts = ax.pie(
        sizes,
        colors=colors,
        startangle=90,
        wedgeprops=dict(width=0.55, edgecolor=_BG, linewidth=2),   # donut style
        counterclock=False,
    )

    # Label bên trong mỗi wedge
    import math
    for wedge, label in zip(wedges, labels):
        rad = math.radians((wedge.theta1 + wedge.theta2) / 2)
        rx  = 0.7 * math.cos(rad)
        ry  = 0.7 * math.sin(rad)
        ax.annotate(
            label,
            xy=(rx, ry),
            ha="center", va="center",
            fontsize=8.5,
            fontweight="bold",
            color=_TEXT_C,
        )

    # Tiêu đề ở giữa donut
    ax.text(
        0, 0, symbol_name,
        ha="center", va="center",
        fontsize=10, fontweight="bold",
        color=_TEXT_C,
    )

    ax.set_title("Sentiment", color=_TEXT_C, fontsize=9, pad=6)
    fig.tight_layout(pad=0.5)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight", facecolor=_BG)
    plt.close(fig)
    buf.seek(0)
    st.image(buf, width="stretch")


def render_outlook_row(
    outlook_data: list[dict],
    chosen_symbols: list[dict],
    n_cols: int = 6,
) -> None:
    """
    Render một hàng các pie chart cho những symbol được chọn ở sidebar.

    Args:
        outlook_data:    Output của get_community_outlook()
        chosen_symbols:  Danh sách symbol dict từ sidebar (có key "symbol")
        n_cols:          Số cột tối đa mỗi hàng
    """
    # Tạo lookup nhanh: tên symbol (upper) → dữ liệu outlook
    lookup = {s["name"].upper(): s for s in outlook_data}

    # Lọc chỉ những symbol được chọn mà có dữ liệu outlook
    matched = []
    for sym in chosen_symbols:
        key = sym["symbol"].upper().replace("/", "").replace("_", "")
        # Thử thêm một vài biến thể tên
        for candidate in [key, key[:6], key.replace(".", "")]:
            if candidate in lookup:
                matched.append((sym["symbol"], lookup[candidate]))
                break

    if not matched:
        st.caption("ℹ️ Không tìm thấy dữ liệu Community Outlook cho các symbol đã chọn.")
        return

    # Chia thành các hàng n_cols cột
    for row_start in range(0, len(matched), n_cols):
        batch = matched[row_start : row_start + n_cols]
        cols  = st.columns(len(batch))
        for col, (sym_name, s) in zip(cols, batch):
            with col:
                render_outlook_pie(
                    symbol_name=sym_name,
                    long_pct=s["longPercentage"],
                    short_pct=s["shortPercentage"],
                )