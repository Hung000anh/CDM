"""
data/queries/news.py
────────────────────
Query news_articles từ Supabase với filter: country, time range, search query.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core import get_client
from core.cache import cache_short
import pandas as pd
from datetime import datetime


@cache_short
def get_news(
    country_ids: tuple[str, ...] | None = None,
    date_from: str | None = None,       # ISO format: "2025-01-01"
    date_to: str | None = None,         # ISO format: "2025-12-31"
    search: str | None = None,          # tìm trong title + description
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """
    Trả về danh sách news articles theo các filter.

    Parameters
    ----------
    country_ids : tuple of str | None
        Lọc theo country_id. None = lấy tất cả.
    date_from : str | None
        Ngày bắt đầu (inclusive), dạng "YYYY-MM-DD".
    date_to : str | None
        Ngày kết thúc (inclusive), dạng "YYYY-MM-DD".
    search : str | None
        Từ khóa tìm kiếm trong title.
    limit : int
        Số bản ghi tối đa mỗi trang.
    offset : int
        Bỏ qua n bản ghi đầu (phân trang).
    """
    client = get_client()

    query = (
        client.table("news_articles")
        .select(
            "id, title, url, description, image_url, published_at, source_domain, "
            "country_id, countries(name, code)"
        )
        .order("published_at", desc=True)
        .limit(limit)
        .offset(offset)
    )

    if country_ids:
        query = query.in_("country_id", list(country_ids))

    if date_from:
        query = query.gte("published_at", f"{date_from}T00:00:00+00:00")

    if date_to:
        query = query.lte("published_at", f"{date_to}T23:59:59+00:00")

    if search and search.strip():
        # Supabase ilike – tìm trong title
        query = query.ilike("title", f"%{search.strip()}%")

    resp = query.execute()
    return resp.data or []


@cache_short
def count_news(
    country_ids: tuple[str, ...] | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    search: str | None = None,
) -> int:
    """Đếm tổng số bản ghi (dùng cho phân trang)."""
    client = get_client()

    query = (
        client.table("news_articles")
        .select("id", count="exact", head=True)
    )

    if country_ids:
        query = query.in_("country_id", list(country_ids))
    if date_from:
        query = query.gte("published_at", f"{date_from}T00:00:00+00:00")
    if date_to:
        query = query.lte("published_at", f"{date_to}T23:59:59+00:00")
    if search and search.strip():
        query = query.ilike("title", f"%{search.strip()}%")

    resp = query.execute()
    return resp.count or 0