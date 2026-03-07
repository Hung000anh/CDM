"""
core/cache.py
─────────────
Wrapper tiện lợi quanh st.cache_data với TTL mặc định.

Lý do tồn tại:
  - Tập trung logic cache vào 1 chỗ; thay đổi TTL không cần sửa từng file.
  - Cung cấp sẵn 3 decorator ứng với 3 mức độ "tươi" của dữ liệu.

Cách dùng:
    from core.cache import cache_medium

    @cache_medium()
    def fetch_something(symbol_id: str):
        ...

Lưu ý:
  - Các hàm được cache PHẢI có tham số hashable (str, int, tuple…).
  - Nếu cần bỏ cache thủ công: gọi <function>.clear() hoặc
    st.cache_data.clear() để xóa toàn bộ.
"""

import functools
import streamlit as st
from config import CACHE_TTL_SHORT, CACHE_TTL_MEDIUM, CACHE_TTL_LONG


def cache_short(func=None, **kwargs):
    """Cache ngắn – phù hợp cho dữ liệu realtime / thay đổi thường xuyên."""
    decorator = st.cache_data(ttl=CACHE_TTL_SHORT, max_entries=30, **kwargs)
    if func is not None:
        return decorator(func)
    return decorator


def cache_medium(func=None, **kwargs):
    """Cache trung bình (10 phút) – phù hợp cho OHLCV daily, COT reports."""
    decorator = st.cache_data(ttl=CACHE_TTL_MEDIUM, max_entries=50, **kwargs)
    if func is not None:
        return decorator(func)
    return decorator


def cache_long(func=None, **kwargs):
    """Cache dài (1 giờ) – phù hợp cho lookup tables ít thay đổi."""
    decorator = st.cache_data(ttl=CACHE_TTL_LONG, max_entries=20, **kwargs)
    if func is not None:
        return decorator(func)
    return decorator


# ── Helper: tắt cache hoàn toàn khi test/debug ──────────────────────────────
def no_cache(func):
    """Decorator giả – không cache, dùng khi debug."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper