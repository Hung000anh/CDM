"""
data/queries/myfxbook.py
────────────────────────
Lấy Community Outlook (Long/Short %) từ bảng trader_sentiments trên Supabase.
Dữ liệu được collector job cập nhật mỗi 4 tiếng.
"""

from core import get_client, cache_medium


@cache_medium
def get_community_outlook() -> list[dict]:
    """
    Trả về danh sách symbol với long/short percentage.

    Returns:
        [
            {"name": "EURUSD", "longPercentage": 58.3, "shortPercentage": 41.7},
            ...
        ]
    """
    client = get_client()
    res = (
        client.table("trader_sentiments")
        .select("long_percent, short_percent, symbols(symbol)")
        .execute()
    )

    rows = []
    for r in (res.data or []):
        symbol = (r.get("symbols") or {}).get("symbol", "")
        if not symbol:
            continue
        # Normalize: bỏ prefix exchange "OANDA:EURUSD" → "EURUSD"
        name = symbol.split(":")[-1].upper()
        rows.append({
            "name":            name,
            "longPercentage":  r["long_percent"],
            "shortPercentage": r["short_percent"],
        })

    return rows