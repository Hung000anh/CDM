"""
pages/03_📅_Economic_Calendar.py
─────────────────────────────────
Economic Calendar page:
  - Hiển thị lịch kinh tế theo ngày
  - Lọc theo currency, impact level
  - Highlight actual vs forecast
  - Navigation qua các ngày
"""

import utils.path_setup  # noqa: F401
import sys
from pathlib import Path
from datetime import date, timedelta, datetime, timezone
import calendar
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
from core import get_client, cache_short

SUPPORT_URL = "https://omg10.com/4/10659204"
BMC_URL     = "https://buymeacoffee.com/hung000anh"
GMAIL       = "hung000anh@gmail.com"

IMPACT_COLORS = {
    "high":    ("#ef4444", "#3d1515"),
    "medium":  ("#f97316", "#3d2010"),
    "low":     ("#6b7280", "#1e1e1e"),
    "holiday": ("#8b5cf6", "#2a1a40"),
}

ALL_CURRENCIES = ["AUD", "CAD", "CHF", "EUR", "GBP", "JPY", "NZD", "USD"]

st.set_page_config(
    page_title="CDM | Economic Calendar",
    page_icon="🫓",
    layout="wide",
)

# ── Global styles ──────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:ital,wght@0,400;0,500;1,400&display=swap');

    html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
    .block-container {{ padding-top: 2rem; }}

    .support-fab {{
        position: fixed; bottom: 60px; right: 24px; z-index: 99999;
        background: linear-gradient(135deg, #f97316, #ef4444);
        color: #ffffff !important; font-size: 15px; font-weight: 700;
        padding: 13px 28px; border-radius: 24px; text-decoration: none !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.45);
        transition: opacity .2s, transform .2s;
    }}
    .support-fab:hover {{ opacity: 0.88; transform: translateY(-2px); }}

    /* ── Calendar table ── */
    .cal-table {{ width: 100%; border-collapse: collapse; }}

    .cal-header {{
        display: grid;
        grid-template-columns: 70px 60px 100px 1fr 90px 90px 90px;
        gap: 0;
        padding: 10px 16px;
        background: #111;
        border-bottom: 1px solid #2a2a2a;
        font-size: 11px; font-weight: 700;
        color: #555; letter-spacing: 1.5px; text-transform: uppercase;
        max-width: 900px;
        margin: 0 auto;
    }}

    .cal-row {{
        display: grid;
        grid-template-columns: 70px 60px 100px 1fr 90px 90px 90px;
        gap: 0;
        padding: 13px 16px;
        border-bottom: 1px solid #1a1a1a;
        align-items: center;
        transition: background .15s;
        max-width: 900px;
        margin: 0 auto;
    }}
    .cal-row:hover {{ background: #161616; }}

    .cal-row.holiday {{
        background: rgba(139,92,246,0.04);
    }}

    .cal-cell {{ font-size: 13px; color: #ccc; }}
    .cal-cell.time {{
        font-family: 'DM Mono', monospace;
        font-size: 12px; color: #666;
    }}
    .cal-cell.event-name {{
        font-size: 13.5px; font-weight: 600; color: #e8e8e8;
        padding-right: 16px;
    }}
    .cal-cell.value {{
        font-family: 'DM Mono', monospace;
        font-size: 13px; text-align: right; padding-right: 24px;
    }}
    .cal-cell.actual-up   {{ color: #22c55e; font-weight: 700; }}
    .cal-cell.actual-down {{ color: #ef4444; font-weight: 700; }}
    .cal-cell.actual-neutral {{ color: #e8e8e8; font-weight: 700; }}
    .cal-cell.forecast {{ color: #888; }}
    .cal-cell.previous {{ color: #555; }}

    /* ── Impact badge ── */
    .impact-badge {{
        display: inline-flex; align-items: center; gap: 4px;
        border-radius: 20px; padding: 3px 10px;
        font-size: 10px; font-weight: 700;
        letter-spacing: .5px; text-transform: uppercase;
        border: 1px solid;
    }}

    /* ── Currency badge ── */
    .currency-badge {{
        display: inline-flex; align-items: center; gap: 5px;
        font-size: 12px; font-weight: 700; color: #e8e8e8;
    }}

    /* ── Day section header ── */
    .day-header {{
        padding: 20px 16px 12px 16px;
        font-family: 'Sora', sans-serif;
        font-size: 18px; font-weight: 800; color: #fff;
        border-bottom: 2px solid #f97316;
        margin-bottom: 0;
        display: flex; align-items: center; gap: 12px;
        max-width: 900px;
        margin: 0 auto;
    }}
    .day-header .day-num {{
        font-size: 36px; font-weight: 900;
        background: linear-gradient(135deg, #f97316, #ef4444);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        line-height: 1;
    }}
    .day-header .day-info {{ display: flex; flex-direction: column; gap: 2px; }}
    .day-header .day-name {{ font-size: 16px; color: #ccc; font-weight: 700; }}
    .day-header .day-count {{ font-size: 12px; color: #555; font-weight: 400; }}

    /* ── Empty ── */
    .empty-day {{
        padding: 24px 16px;
        font-size: 13px; color: #444; font-style: italic;
        max-width: 900px;
        margin: 0 auto;
    }}

    /* ── Summary bar ── */
    .summary-bar {{
        display: flex; gap: 16px; flex-wrap: wrap;
        padding: 16px;
        background: #111; border: 1px solid #1e1e1e; border-radius: 12px;
        margin-bottom: 24px;
        max-width: 900px;
        margin: 0 auto;
    }}
    .summary-item {{
        display: flex; align-items: center; gap: 8px;
        font-size: 13px; color: #888;
    }}
    .summary-dot {{
        width: 10px; height: 10px; border-radius: 50%;
    }}

    /* ── Week nav ── */
    .week-label {{
        text-align: center;
        font-family: 'Sora', sans-serif;
        font-size: 15px; font-weight: 700; color: #e0e0e0;
    }}

    /* ── No data ── */
    .no-events {{
        text-align: center; padding: 60px 0; color: #333;
        font-size: 14px;
    }}
    </style>
    <a class="support-fab" href="{SUPPORT_URL}" target="_blank">🙏 Click ads to Support Me</a>
    """,
    unsafe_allow_html=True,
)


# ── Data layer ─────────────────────────────────────────────────────────────────
@cache_short
def fetch_calendar_week(date_from: str, date_to: str, currencies: tuple, impacts: tuple) -> list[dict]:
    client = get_client()
    q = (
        client.table("economic_calendar")
        .select("id, event_date, event_time, utc_time, currency, event_name, impact_level, actual_value, forecast_value, previous_value, actual_num, forecast_num, previous_num")
        .gte("event_date", date_from)
        .lte("event_date", date_to)
        .order("event_date")
        .order("event_time", nullsfirst=False)
    )
    if currencies:
        q = q.in_("currency", list(currencies))
    if impacts:
        q = q.in_("impact_level", list(impacts))

    res = q.execute()
    return res.data or []


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    today = date.today()

    # ── Date range filter ─────────────────────────────────────────────────────
    st.markdown("**📅 Date Range**")

    # ── Tính giá trị mặc định ──────────────────────────────────────────────────
    last_day = calendar.monthrange(today.year, today.month)[1]

    if "cal_date_from" not in st.session_state:
        st.session_state["cal_date_from"] = today
    if "cal_date_to" not in st.session_state:
        st.session_state["cal_date_to"] = today.replace(day=last_day)

    # ── Quick select buttons ───────────────────────────────────────────────────
    if st.button("Today"):
        st.session_state["cal_date_from"] = today
        st.session_state["cal_date_to"]   = today
    if st.button("This Week"):
        st.session_state["cal_date_from"] = today - timedelta(days=today.weekday())
        st.session_state["cal_date_to"]   = today - timedelta(days=today.weekday()) + timedelta(days=6)
    if st.button("Next Week"):
        next_mon = today - timedelta(days=today.weekday()) + timedelta(days=7)
        st.session_state["cal_date_from"] = next_mon
        st.session_state["cal_date_to"]   = next_mon + timedelta(days=6)
    if st.button("This Month"):
        st.session_state["cal_date_from"] = today.replace(day=1)
        st.session_state["cal_date_to"]   = today.replace(day=last_day)
    if st.button("Next Month"):
        first_next = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        st.session_state["cal_date_from"] = first_next
        st.session_state["cal_date_to"]   = first_next.replace(day=calendar.monthrange(first_next.year, first_next.month)[1])

    # ── Date inputs ────────────────────────────────────────────────────────────
    d_from = st.date_input("From", key="cal_date_from")
    d_to   = st.date_input("To",   key="cal_date_to")

    st.divider()

    # ── Currency filter ───────────────────────────────────────────────────────
    st.markdown("**💱 Currency**")
    selected_currencies = []
    cols2 = st.columns(2)
    for i, cur in enumerate(ALL_CURRENCIES):
        key = f"cal_cur_{cur}"
        st.session_state.setdefault(key, True)
        with cols2[i % 2]:
            if st.checkbox(cur, key=key):
                selected_currencies.append(cur)

    st.divider()

    # ── Impact filter ─────────────────────────────────────────────────────────
    st.markdown("**⚡ Impact**")
    impact_options = {
        "High":    "high",
        "Medium":  "medium",
        "Low":     "low",
        "Holiday":     "holiday",
    }
    selected_impacts = []
    for label, val in impact_options.items():
        key = f"cal_imp_{val}"
        st.session_state.setdefault(key, True)
        if st.checkbox(label, key=key):
            selected_impacts.append(val)

    st.divider()

    # BMC + Contact
    st.markdown(
        f"""
        <a href="{BMC_URL}" target="_blank"
           style="display:block;text-align:center;
                  background:linear-gradient(135deg,#f97316,#ef4444);
                  color:#fff;font-weight:700;font-size:14px;
                  padding:11px 0;border-radius:20px;text-decoration:none;
                  box-shadow:0 4px 12px rgba(0,0,0,0.3);">
            ☕ Buy Me a Coffee
        </a>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div style="margin-top:16px;padding:14px 16px;
                    background:#1a1a1a;border:1px solid #2a2a2a;
                    border-radius:12px;text-align:center;">
            <div style="font-size:11px;color:#666;text-transform:uppercase;
                        letter-spacing:1.5px;margin-bottom:8px;">Contact</div>
            <a href="https://mail.google.com/mail/?view=cm&to={GMAIL}"
               style="display:inline-flex;align-items:center;gap:7px;
                      color:#f97316;font-size:13px;font-weight:600;text-decoration:none;">
                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15"
                     viewBox="0 0 24 24" fill="none" stroke="currentColor"
                     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect width="20" height="16" x="2" y="4" rx="2"/>
                  <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
                </svg>
                {GMAIL}
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="padding: 24px 0 8px 0;">
        <div style="font-size:11px;color:#f97316;font-weight:700;
                    letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">
            Market Intelligence
        </div>
        <h1 style="font-family:'Sora',sans-serif;font-size:38px;
                   font-weight:900;margin:0 0 6px 0;line-height:1.1;">
            📅 Economic Calendar
        </h1>
        <p style="font-size:14px;color:#666;margin:0 0 24px 0;">
            Economic events — Medium, High impact & Holidays across G8 currencies
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Fetch data ──────────────────────────────────────────────────────────────────
if not selected_currencies:
    st.warning("⚠️ Please select at least one currency.")
    st.stop()

if not selected_impacts:
    st.warning("⚠️ Please select at least one impact level.")
    st.stop()

if d_from > d_to:
    st.warning("⚠️ 'From' date must be before or equal to 'To' date.")
    st.stop()

with st.spinner("Loading calendar…"):
    events = fetch_calendar_week(
        date_from=d_from.isoformat(),
        date_to=d_to.isoformat(),
        currencies=tuple(sorted(selected_currencies)),
        impacts=tuple(sorted(selected_impacts)),
    )

# ── Summary bar ────────────────────────────────────────────────────────────────
count_high    = sum(1 for e in events if e.get("impact_level") == "high")
count_medium  = sum(1 for e in events if e.get("impact_level") == "medium")
count_low     = sum(1 for e in events if e.get("impact_level") == "low")
count_holiday = sum(1 for e in events if e.get("impact_level") == "holiday")

st.markdown(
    f"""
    <div class="summary-bar">
        <div class="summary-item">
            <div class="summary-dot" style="background:#ef4444;"></div>
            <span><b style="color:#e0e0e0;">{count_high}</b> High</span>
        </div>
        <div class="summary-item">
            <div class="summary-dot" style="background:#f97316;"></div>
            <span><b style="color:#e0e0e0;">{count_medium}</b> Medium</span>
        </div>
        <div class="summary-item">
            <div class="summary-dot" style="background:#6b7280;"></div>
            <span><b style="color:#e0e0e0;">{count_low}</b> Low</span>
        </div>
        <div class="summary-item">
            <div class="summary-dot" style="background:#8b5cf6;"></div>
            <span><b style="color:#e0e0e0;">{count_holiday}</b> Holiday</span>
        </div>
        <div class="summary-item" style="margin-left:auto;">
            <span style="color:#555;">
                {d_from.strftime('%B %d')} – {d_to.strftime('%B %d, %Y')}
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Group events by day ─────────────────────────────────────────────────────────
from collections import defaultdict

events_by_day: dict[str, list] = defaultdict(list)
for ev in events:
    d = str(ev.get("event_date", ""))[:10]
    if d:
        events_by_day[d].append(ev)

# Generate all days in the selected date range
num_days = (d_to - d_from).days + 1
week_days = [d_from + timedelta(days=i) for i in range(num_days)]


def _fmt_value(val_str, val_num) -> str:
    if val_str and val_str.strip() and val_str.strip() not in ("", "None", "nan"):
        return val_str.strip()
    if val_num is not None:
        return str(val_num)
    return "—"


def _actual_class(actual_num, forecast_num, previous_num) -> str:
    """Determine CSS class for actual value coloring."""
    if actual_num is None:
        return "actual-neutral"
    ref = forecast_num if forecast_num is not None else previous_num
    if ref is None:
        return "actual-neutral"
    if actual_num > ref:
        return "actual-up"
    if actual_num < ref:
        return "actual-down"
    return "actual-neutral"


def _impact_html(impact: str) -> str:
    color, bg = IMPACT_COLORS.get(impact, ("#6b7280", "#1e1e1e"))
    stars = {
        "high":    "HIGH",
        "medium":  "MEDIUM",
        "low":     "LOW",
        "holiday": "HOLIDAY",
    }.get(impact, "☆")
    return (
        f'<span class="impact-badge" '
        f'style="color:{color};background:{bg};border-color:{color}33;">'
        f'{stars}</span>'
    )


# ── Render table header ─────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="cal-header">
        <div>Time</div>
        <div>CCY</div>
        <div>Impact</div>
        <div>Event</div>
        <div style="text-align:right;padding-right:24px;">Actual</div>
        <div style="text-align:right;padding-right:24px;">Forecast</div>
        <div style="text-align:right;padding-right:24px;">Previous</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Render each day ─────────────────────────────────────────────────────────────
has_any = False

for day in week_days:
    day_str   = day.isoformat()
    day_evts  = events_by_day.get(day_str, [])
    is_today  = (day == today)
    is_wknd   = day.weekday() >= 5

    today_badge = (
        '<span style="background:linear-gradient(135deg,#f97316,#ef4444);'
        'color:#fff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;'
        'letter-spacing:.5px;">TODAY</span>'
        if is_today else ""
    )

    count_label = f"{len(day_evts)} event{'s' if len(day_evts) != 1 else ''}" if day_evts else "No events"

    day_color = "#2a2a2a" if is_wknd else "#111"
    st.markdown(
        f"""
        <div class="day-header" style="background:{day_color};">
            <div class="day-num">{day.day:02d}</div>
            <div class="day-info">
                <div class="day-name">{day.strftime('%A, %B %Y')} {today_badge}</div>
                <div class="day-count">{count_label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not day_evts:
        st.markdown('<div class="empty-day">No events for this day.</div>', unsafe_allow_html=True)
        continue

    has_any = True
    rows_html = []
    for ev in day_evts:
        impact   = (ev.get("impact_level") or "low").lower()
        currency = ev.get("currency", "")
        name     = ev.get("event_name", "")

        # Time
        t = ev.get("event_time") or ""
        if t and len(str(t)) >= 5:
            time_str = str(t)[:5]
        else:
            time_str = "All day"

        # Values
        actual_str   = _fmt_value(ev.get("actual_value"),   ev.get("actual_num"))
        forecast_str = _fmt_value(ev.get("forecast_value"), ev.get("forecast_num"))
        previous_str = _fmt_value(ev.get("previous_value"), ev.get("previous_num"))
        actual_cls   = _actual_class(ev.get("actual_num"), ev.get("forecast_num"), ev.get("previous_num"))

        row_cls = "cal-row holiday" if impact == "holiday" else "cal-row"

        rows_html.append(
            f'<div class="{row_cls}">'
            f'  <div class="cal-cell time">{time_str}</div>'
            f'  <div class="cal-cell"><span class="currency-badge">{currency}</span></div>'
            f'  <div class="cal-cell">{_impact_html(impact)}</div>'
            f'  <div class="cal-cell event-name">{name}</div>'
            f'  <div class="cal-cell value {actual_cls}">{actual_str}</div>'
            f'  <div class="cal-cell value forecast">{forecast_str}</div>'
            f'  <div class="cal-cell value previous">{previous_str}</div>'
            f'</div>'
        )

    st.markdown("".join(rows_html), unsafe_allow_html=True)

if not has_any:
    st.markdown(
        """
        <div class="no-events">
            <div style="font-size:48px;margin-bottom:16px;">📭</div>
            <p>No events found for this date range with current filters.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Legend ──────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="display:flex;gap:24px;flex-wrap:wrap;padding:16px;
                background:#0d0d0d;border:1px solid #1a1a1a;border-radius:12px;
                font-size:12px;color:#555;max-width:900px;margin:0 auto;">
        <span><b style="color:#22c55e;">Green actual</b> = better than forecast/previous</span>
        <span><b style="color:#ef4444;">Red actual</b> = worse than forecast/previous</span>
        <span><b style="color:#e8e8e8;">White actual</b> = in line / no forecast</span>
        <span style="margin-left:auto;">All times in GMT-5</span>
    </div>
    """,
    unsafe_allow_html=True,
)
# ── Footer ──────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    f"<center style='color:#555;padding:12px 0 24px 0;font-size:13px;'>"
    f"CDM © 2026 &nbsp;·&nbsp; Built with Streamlit &nbsp;·&nbsp; "
    f"<a href='{SUPPORT_URL}' style='color:#f97316;text-decoration:none;'>🙏 Click ads to Support Me</a>"
    f"</center>",
    unsafe_allow_html=True,
)