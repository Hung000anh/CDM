"""
config/settings.py
──────────────────
Load environment variables and declare shared constants for the app.
Supports both local .env and Streamlit Cloud Secrets.
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def _get(key: str) -> str:
    """Read from Streamlit Secrets first, fall back to environment variable."""
    return st.secrets.get(key) or os.environ.get(key, "")

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL: str = _get("SUPABASE_URL")
SUPABASE_KEY: str = _get("SUPABASE_KEY")


# ── Cache TTL (seconds) ───────────────────────────────────────────────────────
CACHE_TTL_SHORT  = 60        # frequently changing data (realtime prices)
CACHE_TTL_MEDIUM = 60 * 10   # 10 minutes – daily data
CACHE_TTL_LONG   = 60 * 60   # 1 hour – lookup tables (symbols, timeframes…)

# ── Supabase pagination ───────────────────────────────────────────────────────
DEFAULT_PAGE_SIZE = 1_000    # Supabase default row limit per request
MAX_ROWS          = 10_000   # hard cap to avoid overloading

# ── Supported timeframes (must match timeframes table in DB) ──────────────────
SUPPORTED_TIMEFRAMES = ["1D", "1W", "1M", "3M", "12M"]

TIMEFRAME_LABELS = {
    "1D":  "1 Day",
    "1W":  "1 Week",
    "1M":  "1 Month",
    "3M":  "3 Months",
    "12M": "12 Months",
}

TIMEFRAME_DAYS = {
    "1D":  60,
    "1W":  365,
    "1M":  1800,
    "3M":  3650,
    "12M": 7300,
}

# ── Chart colors ──────────────────────────────────────────────────────────────
COLOR_BULL    = "#ffffff"   # bullish candle
COLOR_BEAR    = "#388e3c"   # bearish candle
COLOR_LINE    = "#f97316"   # line chart (Economic indicators)
COLOR_NONCOMM = "#2196F3"   # Non-commercial (speculators)
COLOR_COMM    = "#FF9800"   # Commercial (hedgers)
COLOR_NONREP  = "#9E9E9E"   # Non-reportable (small traders)
COLOR_VOLUME  = "#7E57C2"   # Volume bar