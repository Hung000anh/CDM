"""
data/queries/symbols.py
───────────────────────
Query các lookup tables: asset_types, symbols, timeframes available per symbol.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core import get_client, cache_long


@cache_long
def get_asset_types() -> list[dict]:
    client = get_client()
    res = client.table("asset_types").select("id, name").order("name").execute()
    return res.data or []


@cache_long
def get_countries() -> list[dict]:
    """Trả về danh sách tất cả countries, sắp xếp theo tên."""
    client = get_client()
    res = client.table("countries").select("id, name").order("name").execute()
    return res.data or []


@cache_long
def get_symbols_by_asset_type(asset_type_id: str) -> list[dict]:
    client = get_client()
    res = (
        client.table("symbols")
        .select("id, symbol, name, cftc_contract_id, country_id, exchanges(name)")
        .eq("asset_type_id", asset_type_id)
        .order("symbol")
        .execute()
    )
    rows = []
    for r in (res.data or []):
        rows.append({
            "id": r["id"],
            "symbol": r["symbol"],
            "name": r["name"],
            "cftc_contract_id": r.get("cftc_contract_id"),
            "country_id": r.get("country_id"),
            "exchange": (r.get("exchanges") or {}).get("name", ""),
        })
    return rows


@cache_long
def get_symbols_by_country(asset_type_id: str, country_id: str) -> list[dict]:
    """
    Trả về symbols thuộc asset_type_id VÀ country_id chỉ định.
    Dùng cho Economic asset type khi user chọn country.
    """
    client = get_client()
    res = (
        client.table("symbols")
        .select("id, symbol, name, cftc_contract_id, country_id, exchanges(name)")
        .eq("asset_type_id", asset_type_id)
        .eq("country_id", country_id)
        .order("symbol")
        .execute()
    )
    rows = []
    for r in (res.data or []):
        rows.append({
            "id": r["id"],
            "symbol": r["symbol"],
            "name": r["name"],
            "cftc_contract_id": r.get("cftc_contract_id"),
            "country_id": r.get("country_id"),
            "exchange": (r.get("exchanges") or {}).get("name", ""),
        })
    return rows


@cache_long
def get_timeframes_by_symbol(symbol_id: str) -> list[dict]:
    """
    Trả về danh sách timeframes thực tế có trong symbol_timeframes cho symbol này.
    Sắp xếp theo thứ tự: 1D → 1W → 1M → 3M → 12M
    """
    client = get_client()
    res = (
        client.table("symbol_timeframes")
        .select("id, timeframes(id, name)")
        .eq("symbol_id", symbol_id)
        .execute()
    )
    ORDER = ["1D", "1W", "1M", "3M", "12M"]
    rows = []
    for r in (res.data or []):
        tf = r.get("timeframes") or {}
        if tf.get("name"):
            rows.append({
                "symbol_timeframe_id": r["id"],
                "timeframe_id": tf["id"],
                "name": tf["name"],
            })
    rows.sort(key=lambda x: ORDER.index(x["name"]) if x["name"] in ORDER else 99)
    return rows