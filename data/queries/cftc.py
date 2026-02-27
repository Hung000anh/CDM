"""
data/queries/cftc.py
────────────────────
Fetch bảng cftc_reports từ Supabase và tính COT Index.
"""

import sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd
from core import get_client, cache_medium


@cache_medium
def get_cftc_reports(cftc_contract_id: int) -> pd.DataFrame:
    """Fetch toàn bộ cftc_reports cho 1 contract, cache 10 phút."""
    client = get_client()
    all_rows: list[dict] = []
    offset = 0
    page = 1000

    while True:
        res = (
            client.table("cftc_reports")
            .select("*")
            .eq("cftc_contract_id", cftc_contract_id)
            .order("report_date", desc=False)
            .range(offset, offset + page - 1)
            .execute()
        )
        batch = res.data or []
        all_rows.extend(batch)
        if len(batch) < page:
            break
        offset += page

    if not all_rows:
        return pd.DataFrame()

    return pd.DataFrame(all_rows)


def add_cot_index(cot_df: pd.DataFrame, weeks: int = 26) -> pd.DataFrame:
    """
    Tính COT Index (0-100) cho 3 nhóm: commercial, large (non-commercial), retail.

    Returns DataFrame với các cột bổ sung:
        net_commercial, net_large, net_retail
        adj_commercial, adj_large, adj_retail
        cot_index_commercial, cot_index_large, cot_index_retail
    """
    if cot_df.empty:
        return cot_df

    df = cot_df.copy()
    df["report_date"] = pd.to_datetime(df["report_date"])

    # Resample tuần W-FRI
    df_weekly = (
        df.set_index("report_date")
        .resample("W-FRI")
        .last()
        .dropna(how="all")
        .reset_index()
    )

    # Net positions
    df_weekly["net_commercial"] = df_weekly["commercial_long"]    - df_weekly["commercial_short"]
    df_weekly["net_large"]      = df_weekly["noncommercial_long"] - df_weekly["noncommercial_short"]
    df_weekly["net_retail"]     = df_weekly["nonreportable_long"] - df_weekly["nonreportable_short"]

    # Chuẩn hóa theo open interest
    df_weekly["open_interest_all"] = df_weekly["open_interest_all"].replace(0, np.nan)
    df_weekly["adj_commercial"]    = df_weekly["net_commercial"] / df_weekly["open_interest_all"]
    df_weekly["adj_large"]         = df_weekly["net_large"]      / df_weekly["open_interest_all"]
    df_weekly["adj_retail"]        = df_weekly["net_retail"]     / df_weekly["open_interest_all"]

    # COT Index 0-100
    def calc_index(series: pd.Series) -> pd.Series:
        min_v = series.rolling(window=weeks, min_periods=1).min()
        max_v = series.rolling(window=weeks, min_periods=1).max()
        idx   = 100 * (series - min_v) / (max_v - min_v)
        idx[max_v == min_v] = np.nan
        return idx

    df_weekly["cot_index_commercial"] = calc_index(df_weekly["adj_commercial"])
    df_weekly["cot_index_large"]      = calc_index(df_weekly["adj_large"])
    df_weekly["cot_index_retail"]     = calc_index(df_weekly["adj_retail"])

    return df_weekly


def add_net_noncommercial(df: pd.DataFrame) -> pd.DataFrame:
    """Thêm cột net_noncommercial = noncommercial_long - noncommercial_short."""
    df = df.copy()
    df["net_noncommercial"] = df["noncommercial_long"] - df["noncommercial_short"]
    return df


def get_cot_data(cftc_contract_id: int, weeks: int = 26) -> pd.DataFrame:
    """Shortcut: fetch + tính COT index + net noncommercial trong 1 lần gọi."""
    df_raw = get_cftc_reports(cftc_contract_id)
    if df_raw.empty:
        return df_raw
    df = add_cot_index(df_raw, weeks=weeks)
    df = add_net_noncommercial(df)
    return df