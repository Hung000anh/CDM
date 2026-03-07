"""
data/queries/prices.py
──────────────────────
Fetch toàn bộ OHLCV data (không giới hạn ngày).
Việc cắt theo TIMEFRAME_DAYS được thực hiện ở tầng hiển thị (candlestick.py).
"""

import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
from core import get_client, cache_medium
from config import DEFAULT_PAGE_SIZE


@cache_medium
def get_prices(
    symbol_timeframe_id: str,
    timeframe_name: str,
    limit: int = 500,
) -> pd.DataFrame:
    """
    Trả về OHLCV DataFrame, giới hạn số nến gần nhất.

    Args:
        symbol_timeframe_id: UUID từ bảng symbol_timeframes
        timeframe_name:      Tên timeframe – dùng làm cache key
        limit:               Số nến tối đa lấy về (mặc định 2000)
    """
    client = get_client()

    all_rows: list[dict] = []
    offset = 0
    remaining = limit

    while remaining > 0:
        page_size = min(DEFAULT_PAGE_SIZE, remaining)
        res = (
            client.table("prices")
            .select("timestamp, open, high, low, close, volume")
            .eq("symbol_timeframe_id", symbol_timeframe_id)
            .order("timestamp", desc=True)   # lấy mới nhất trước
            .range(offset, offset + page_size - 1)
            .execute()
        )
        batch = res.data or []
        all_rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
        remaining -= page_size

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Đảo lại thứ tự tăng dần theo thời gian
    return df.sort_values("timestamp").reset_index(drop=True)