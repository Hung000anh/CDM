"""
pages/03_📅_Economic_Calendar.py
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
import pytz
from core import get_client, cache_short

# Base timezone of data in DB
DB_TZ = pytz.timezone("America/New_York")  # GMT-5 / EST — data stored in this tz

TIMEZONE_OPTIONS = {
    "GMT-5  (New York / EST)":        "America/New_York",
    "GMT+0  (London / UTC)":          "Europe/London",
    "GMT+1  (Paris / CET)":           "Europe/Paris",
    "GMT+3  (Moscow)":                "Europe/Moscow",
    "GMT+5  (Karachi)":               "Asia/Karachi",
    "GMT+7  (Bangkok / Ho Chi Minh)": "Asia/Bangkok",
    "GMT+8  (Singapore / HKT)":       "Asia/Singapore",
    "GMT+9  (Tokyo / JST)":           "Asia/Tokyo",
    "GMT+10 (Sydney / AEST)":         "Australia/Sydney",
    "GMT+12 (Auckland)":              "Pacific/Auckland",
}

def convert_time(time_str: str, target_tz_name: str) -> str:
    """Convert HH:MM from DB_TZ (EST/EDT aware) to target timezone."""
    if not time_str or time_str in ("All day", "—"):
        return time_str
    try:
        h, m = int(time_str[:2]), int(time_str[3:5])
        today_dt = datetime.now(DB_TZ).date()
        naive_dt = datetime(today_dt.year, today_dt.month, today_dt.day, h, m)
        localized = DB_TZ.localize(naive_dt, is_dst=None)
        converted = localized.astimezone(pytz.timezone(target_tz_name))
        return converted.strftime("%H:%M")
    except Exception:
        return time_str

def convert_session_hour(hour: int, target_tz_name: str) -> str:
    """Convert session boundary hour from DB_TZ (DST aware) to target tz."""
    try:
        today_dt = datetime.now(DB_TZ).date()
        naive_dt = datetime(today_dt.year, today_dt.month, today_dt.day, hour % 24, 0)
        localized = DB_TZ.localize(naive_dt, is_dst=None)
        converted = localized.astimezone(pytz.timezone(target_tz_name))
        return converted.strftime("%H:%M")
    except Exception:
        return f"{hour:02d}:00"

SUPPORT_URL = "https://omg10.com/4/10659204"
BMC_URL     = "https://buymeacoffee.com/hung000anh"
GMAIL       = "hung000anh@gmail.com"

IMPACT_COLORS = {
    "high":    ("#ef4444", "#3d1515", "rgba(239,68,68,0.05)",    "#ef4444"),
    "medium":  ("#eab308", "#2d2500", "rgba(234,179,8,0.05)",    "#eab308"),
    "low":     ("#6b7280", "#1e1e1e", "transparent",             "#6b7280"),
    "holiday": ("#8b5cf6", "#2a1a40", "rgba(139,92,246,0.06)",   "#8b5cf6"),
}

ALL_CURRENCIES = ["AUD", "CAD", "CHF", "EUR", "GBP", "JPY", "NZD", "USD"]

CURRENCY_COUNTRY = {
    "AUD": "au", "CAD": "ca", "CHF": "ch", "EUR": "eu",
    "GBP": "gb", "JPY": "jp", "NZD": "nz", "USD": "us",
}

def flag_img(currency: str, size: int = 20) -> str:
    code = CURRENCY_COUNTRY.get(currency, "")
    if not code:
        return ""
    url = f"https://flagcdn.com/w40/{code}.png"
    return (
        f'<img src="{url}" width="{size}" height="{size}" '
        f'style="border-radius:50%;object-fit:cover;vertical-align:middle;'
        f'border:1px solid rgba(255,255,255,0.1);" />'
    )

st.set_page_config(page_title="CDM | Economic Calendar", page_icon="🫓", layout="wide")

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
        box-shadow: 0 4px 14px rgba(0,0,0,0.45); transition: opacity .2s, transform .2s;
    }}
    .support-fab:hover {{ opacity: 0.88; transform: translateY(-2px); }}

    /* ── Table wrapper: scroll ngang trên mobile ── */
    .cal-table-wrapper {{
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        border-radius: 0 0 8px 8px;
    }}

    .cal-header {{
        display: grid;
        grid-template-columns: 70px 60px 100px 1fr 90px 90px 90px;
        min-width: 580px;
        padding: 10px 16px;
        background: #111; border-bottom: 1px solid #2a2a2a;
        font-size: 11px; font-weight: 700;
        color: #555; letter-spacing: 1.5px; text-transform: uppercase;
    }}
    .cal-row {{
        display: grid;
        grid-template-columns: 70px 60px 100px 1fr 90px 90px 90px;
        min-width: 580px;
        padding: 13px 16px;
        border-bottom: 1px solid #1a1a1a;
        align-items: center;
        border-right: 1px solid transparent;
        border-top: 1px solid transparent;
        transition: filter .2s, transform .2s, box-shadow .2s;
    }}
    .cal-row:hover {{
        filter: brightness(1.3); transform: translateX(5px);
        box-shadow: -4px 0 16px rgba(255,255,255,0.05);
        border-top: 1px solid rgba(255,255,255,0.07);
        border-bottom: 1px solid rgba(255,255,255,0.07);
        border-right: 1px solid rgba(255,255,255,0.07);
        cursor: default;
    }}
    .cal-cell {{ font-size: 13px; color: #ccc; }}
    .cal-cell.time {{ font-family: 'DM Mono', monospace; font-size: 12px; color: #666; }}
    .cal-cell.event-name {{ font-size: 13.5px; font-weight: 600; color: #e8e8e8; padding-right: 16px; }}
    .cal-cell.value {{ font-family: 'DM Mono', monospace; font-size: 13px; text-align: right; padding-right: 24px; }}
    .cal-cell.actual-up   {{ color: #22c55e; font-weight: 700; }}
    .cal-cell.actual-down {{ color: #ef4444; font-weight: 700; }}
    .cal-cell.actual-neutral {{ color: #e8e8e8; font-weight: 700; }}
    .cal-cell.forecast {{ color: #888; }}
    .cal-cell.previous {{ color: #555; }}
    .impact-badge {{
        display: inline-flex; align-items: center; gap: 4px;
        border-radius: 20px; padding: 3px 10px;
        font-size: 10px; font-weight: 700;
        letter-spacing: .5px; text-transform: uppercase; border: 1px solid;
    }}
    .currency-badge {{ display: inline-flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 700; color: #e8e8e8; }}
    .day-header {{
        padding: 20px 16px 12px 16px;
        font-family: 'Sora', sans-serif; font-size: 18px; font-weight: 800; color: #fff;
        border-bottom: 2px solid #f97316;
        display: flex; align-items: center; gap: 12px;
    }}
    .day-header .day-num {{
        font-size: 36px; font-weight: 900;
        background: linear-gradient(135deg, #f97316, #ef4444);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1;
    }}
    .day-header .day-info {{ display: flex; flex-direction: column; gap: 2px; }}
    .day-header .day-name {{ font-size: 16px; color: #ccc; font-weight: 700; }}
    .day-header .day-count {{ font-size: 12px; color: #555; font-weight: 400; }}
    .empty-day {{ padding: 24px 16px; font-size: 13px; color: #444; font-style: italic; }}
    .summary-bar {{
        display: flex; gap: 16px; flex-wrap: wrap; padding: 16px;
        background: #111; border: 1px solid #1e1e1e; border-radius: 12px; margin-bottom: 24px;
    }}
    .summary-item {{ display: flex; align-items: center; gap: 8px; font-size: 13px; color: #888; }}
    .summary-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
    .no-events {{ text-align: center; padding: 60px 0; color: #333; font-size: 14px; }}

    /* ── Mobile responsive ── */
    @media (max-width: 768px) {{
        .day-header {{ padding: 14px 10px 10px 10px; gap: 8px; }}
        .day-header .day-num {{ font-size: 26px; }}
        .day-header .day-name {{ font-size: 13px; }}
        .day-header .day-count {{ font-size: 11px; }}
        .support-fab {{ font-size: 13px; padding: 10px 18px; bottom: 16px; right: 12px; }}
        .summary-bar {{ gap: 10px; padding: 12px; }}
        .summary-item {{ font-size: 12px; }}
    }}
    </style>
    <a class="support-fab" href="{SUPPORT_URL}" target="_blank">🙏 Click ads to Support Me</a>
    """,
    unsafe_allow_html=True,
)


@cache_short
def fetch_calendar_week(date_from, date_to, currencies, impacts):
    client = get_client()
    q = (
        client.table("economic_calendar")
        .select("id,event_date,event_time,utc_time,currency,event_name,impact_level,actual_value,forecast_value,previous_value,actual_num,forecast_num,previous_num")
        .gte("event_date", date_from).lte("event_date", date_to)
        .order("event_date").order("event_time", nullsfirst=False)
    )
    if currencies: q = q.in_("currency", list(currencies))
    if impacts:    q = q.in_("impact_level", list(impacts))
    return q.execute().data or []


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    today    = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]

    st.markdown("**📅 Date Range**")
    if "cal_date_from" not in st.session_state:
        st.session_state["cal_date_from"] = today
    if "cal_date_to" not in st.session_state:
        st.session_state["cal_date_to"] = today.replace(day=last_day)

    b1, b2 = st.columns(2)
    with b1:
        if st.button("Today", use_container_width=True):
            st.session_state["cal_date_from"] = today
            st.session_state["cal_date_to"]   = today
    with b2:
        if st.button("Next Day", use_container_width=True):
            tomorrow = today + timedelta(days=1)
            st.session_state["cal_date_from"] = tomorrow
            st.session_state["cal_date_to"]   = tomorrow

    b3, b4 = st.columns(2)
    with b3:
        if st.button("This Week", use_container_width=True):
            st.session_state["cal_date_from"] = today - timedelta(days=today.weekday())
            st.session_state["cal_date_to"]   = today - timedelta(days=today.weekday()) + timedelta(days=6)
    with b4:
        if st.button("Next Week", use_container_width=True):
            next_mon = today - timedelta(days=today.weekday()) + timedelta(days=7)
            st.session_state["cal_date_from"] = next_mon
            st.session_state["cal_date_to"]   = next_mon + timedelta(days=6)

    b5, b6 = st.columns(2)
    with b5:
        if st.button("This Month", use_container_width=True):
            st.session_state["cal_date_from"] = today.replace(day=1)
            st.session_state["cal_date_to"]   = today.replace(day=last_day)
    with b6:
        if st.button("Next Month", use_container_width=True):
            first_next = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
            st.session_state["cal_date_from"] = first_next
            st.session_state["cal_date_to"]   = first_next.replace(day=calendar.monthrange(first_next.year, first_next.month)[1])

    d_from = st.date_input("From", key="cal_date_from")
    d_to   = st.date_input("To",   key="cal_date_to")
    st.divider()

    st.markdown("**💱 Currency**")
    for cur in ALL_CURRENCIES:
        if f"cal_cur_{cur}" not in st.session_state:
            st.session_state[f"cal_cur_{cur}"] = True
    selected_currencies = []
    cols2 = st.columns(2)
    for i, cur in enumerate(ALL_CURRENCIES):
        with cols2[i % 2]:
            if st.checkbox(cur, key=f"cal_cur_{cur}"):
                selected_currencies.append(cur)
    st.divider()

    st.markdown("**⚡ Impact**")
    impact_options = {"High": "high", "Medium": "medium", "Low": "low", "Holiday": "holiday"}
    selected_impacts = []
    for label, val in impact_options.items():
        st.session_state.setdefault(f"cal_imp_{val}", True)
        if st.checkbox(label, key=f"cal_imp_{val}"):
            selected_impacts.append(val)
    st.divider()

    st.markdown("**🌐 Timezone**")
    tz_labels = list(TIMEZONE_OPTIONS.keys())
    _default_tz_idx = tz_labels.index("GMT+7  (Bangkok / Ho Chi Minh)")
    selected_tz_label = st.selectbox(
        "Display timezone",
        options=tz_labels,
        index=_default_tz_idx,
        label_visibility="collapsed",
        key="cal_timezone",
    )
    selected_tz = TIMEZONE_OPTIONS[selected_tz_label]
    st.divider()

    st.markdown(
        f'<a href="{BMC_URL}" target="_blank" style="display:block;text-align:center;'
        f'background:linear-gradient(135deg,#f97316,#ef4444);color:#fff;font-weight:700;'
        f'font-size:14px;padding:11px 0;border-radius:20px;text-decoration:none;">☕ Buy Me a Coffee</a>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="margin-top:16px;padding:14px 16px;background:#1a1a1a;border:1px solid #2a2a2a;'
        f'border-radius:12px;text-align:center;">'
        f'<div style="font-size:11px;color:#666;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">Contact</div>'
        f'<a href="https://mail.google.com/mail/?view=cm&to={GMAIL}" style="color:#f97316;font-size:13px;font-weight:600;text-decoration:none;">{GMAIL}</a>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="padding:24px 0 8px 0;">
        <div style="font-size:11px;color:#f97316;font-weight:700;letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">Market Intelligence</div>
        <h1 style="font-family:'Sora',sans-serif;font-size:38px;font-weight:900;margin:0 0 6px 0;line-height:1.1;">📅 Economic Calendar</h1>
        <p style="font-size:14px;color:#666;margin:0 0 24px 0;">Economic events — Medium, High impact & Holidays across G8 currencies</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not selected_currencies:
    st.warning("⚠️ Please select at least one currency."); st.stop()
if not selected_impacts:
    st.warning("⚠️ Please select at least one impact level."); st.stop()
if d_from > d_to:
    st.warning("⚠️ 'From' date must be before or equal to 'To' date."); st.stop()

with st.spinner("Loading calendar…"):
    events = fetch_calendar_week(
        date_from=d_from.isoformat(), date_to=d_to.isoformat(),
        currencies=tuple(sorted(selected_currencies)),
        impacts=tuple(sorted(selected_impacts)),
    )

count_high    = sum(1 for e in events if e.get("impact_level") == "high")
count_medium  = sum(1 for e in events if e.get("impact_level") == "medium")
count_low     = sum(1 for e in events if e.get("impact_level") == "low")
count_holiday = sum(1 for e in events if e.get("impact_level") == "holiday")

st.markdown(
    f"""
    <div class="summary-bar">
        <div class="summary-item"><div class="summary-dot" style="background:#ef4444;"></div><span><b style="color:#e0e0e0;">{count_high}</b> High</span></div>
        <div class="summary-item"><div class="summary-dot" style="background:#eab308;"></div><span><b style="color:#e0e0e0;">{count_medium}</b> Medium</span></div>
        <div class="summary-item"><div class="summary-dot" style="background:#6b7280;"></div><span><b style="color:#e0e0e0;">{count_low}</b> Low</span></div>
        <div class="summary-item"><div class="summary-dot" style="background:#8b5cf6;"></div><span><b style="color:#e0e0e0;">{count_holiday}</b> Holiday</span></div>
        <div class="summary-item" style="margin-left:auto;"><span style="color:#555;">{d_from.strftime('%B %d')} – {d_to.strftime('%B %d, %Y')}</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

from collections import defaultdict
events_by_day: dict[str, list] = defaultdict(list)
for ev in events:
    d = str(ev.get("event_date", ""))[:10]
    if d: events_by_day[d].append(ev)

num_days  = (d_to - d_from).days + 1
week_days = [d_from + timedelta(days=i) for i in range(num_days)]


def _fmt_value(val_str, val_num) -> str:
    if val_str and val_str.strip() and val_str.strip() not in ("", "None", "nan"):
        return val_str.strip()
    if val_num is not None:
        return str(val_num)
    return "—"

def _actual_class(actual_num, forecast_num, previous_num) -> str:
    if actual_num is None: return "actual-neutral"
    ref = forecast_num if forecast_num is not None else previous_num
    if ref is None: return "actual-neutral"
    if actual_num > ref: return "actual-up"
    if actual_num < ref: return "actual-down"
    return "actual-neutral"

def _impact_html(impact: str) -> str:
    text_color, badge_bg, _row_bg, border = IMPACT_COLORS.get(impact, ("#6b7280", "#1e1e1e", "transparent", "#6b7280"))
    labels = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW", "holiday": "HOLIDAY"}
    return (
        f'<span class="impact-badge" style="color:{text_color};background:{badge_bg};border-color:{border};">'
        f'{labels.get(impact, impact.upper())}</span>'
    )


# ── Main layout: legend | calendar | right ────────────────────────────────────
legend_col, cal_col, right_col = st.columns([1, 5, 1])

with legend_col:
    tz_short = selected_tz_label.split("(")[0].strip()

    st.markdown(
        f"""
        <div style="background:#0d0d0d;border:1px solid #1e1e1e;border-radius:12px;padding:18px 14px;">

          <div style="font-size:12px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#666;margin-bottom:16px;">📖 Guide</div>

          <div style="font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#666;margin-bottom:10px;">Impact Level</div>

          <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:18px;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="border-radius:20px;padding:2px 8px;font-size:10px;font-weight:700;text-transform:uppercase;border:1px solid #ef4444;color:#ef4444;background:rgba(239,68,68,0.12);white-space:nowrap;">HIGH</span>
              <span style="font-size:12px;color:#888;line-height:1.4;">Market-moving, avoid trading</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="border-radius:20px;padding:2px 8px;font-size:10px;font-weight:700;text-transform:uppercase;border:1px solid #eab308;color:#eab308;background:rgba(234,179,8,0.12);white-space:nowrap;">MEDIUM</span>
              <span style="font-size:12px;color:#888;line-height:1.4;">Moderate, watch for spikes</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="border-radius:20px;padding:2px 8px;font-size:10px;font-weight:700;text-transform:uppercase;border:1px solid #6b7280;color:#6b7280;background:rgba(107,114,128,0.12);white-space:nowrap;">LOW</span>
              <span style="font-size:12px;color:#888;line-height:1.4;">Minor impact</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="border-radius:20px;padding:2px 8px;font-size:10px;font-weight:700;text-transform:uppercase;border:1px solid #8b5cf6;color:#8b5cf6;background:rgba(139,92,246,0.12);white-space:nowrap;">HOLIDAY</span>
              <span style="font-size:12px;color:#888;line-height:1.4;">Low liquidity day</span>
            </div>
          </div>

          <div style="border-top:1px solid #1e1e1e;margin-top:14px;padding-top:10px;font-size:12px;color:#555;">
            All times {tz_short}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Sessions box ──────────────────────────────────────────────────────────
    SESSIONS = [
        ("au", "Sydney",    20,  5),
        ("jp", "Tokyo",     19,  4),
        ("gb", "London",     3, 12),
        ("us", "New York",   8, 17),
    ]

    session_rows = ""
    for code, name, s, e in SESSIONS:
        flag_tag = (
            f'<img src="https://flagcdn.com/w40/{code}.png" width="20" height="20" '
            f'style="border-radius:50%;object-fit:cover;vertical-align:middle;'
            f'border:1px solid rgba(255,255,255,0.1);" />'
        )
        s_str = convert_session_hour(s, selected_tz)
        e_str = convert_session_hour(e, selected_tz)
        session_rows += (
            f'<div style="display:flex;align-items:center;justify-content:space-between;'
            f'padding:7px 0;border-bottom:1px solid #1a1a1a;">'
            f'  <div style="display:flex;align-items:center;gap:7px;">'
            f'    {flag_tag}'
            f'    <span style="font-size:12px;font-weight:600;color:#ccc;">{name}</span>'
            f'  </div>'
            f'  <span style="font-family:DM Mono,monospace;font-size:11px;color:#666;">'
            f'{s_str} – {e_str}</span>'
            f'</div>'
        )

    st.markdown(
        f'<div style="background:#0d0d0d;border:1px solid #1e1e1e;border-radius:12px;padding:18px 14px;">'
        f'<div style="font-size:12px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#666;margin-bottom:12px;">🕐 Sessions</div>'
        f'{session_rows}'
        f'<div style="font-size:10px;color:#444;margin-top:8px;">{tz_short}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="background:#0d0d0d;border:1px solid #1e1e1e;border-radius:12px;padding:18px 14px;">'
        '<div style="font-size:12px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#666;margin-bottom:12px;">🎨 Actual Color</div>'
        '<div style="display:flex;flex-direction:column;gap:8px;">'
        '  <div style="display:flex;align-items:flex-start;gap:8px;">'
        '    <span style="width:8px;height:8px;border-radius:50%;background:#22c55e;flex-shrink:0;margin-top:3px;"></span>'
        '    <span style="font-size:12px;color:#888;line-height:1.5;">Better than forecast → bullish</span>'
        '  </div>'
        '  <div style="display:flex;align-items:flex-start;gap:8px;">'
        '    <span style="width:8px;height:8px;border-radius:50%;background:#ef4444;flex-shrink:0;margin-top:3px;"></span>'
        '    <span style="font-size:12px;color:#888;line-height:1.5;">Worse than forecast → bearish</span>'
        '  </div>'
        '  <div style="display:flex;align-items:flex-start;gap:8px;">'
        '    <span style="width:8px;height:8px;border-radius:50%;background:#666;flex-shrink:0;margin-top:3px;"></span>'
        '    <span style="font-size:12px;color:#888;line-height:1.5;">In line / no forecast</span>'
        '  </div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

with cal_col:
    # ── Table header wrapped in scroll container ───────────────────────────────
    st.markdown(
        """
        <div class="cal-table-wrapper">
        <div class="cal-header">
            <div>Time</div><div>CCY</div><div>Impact</div><div>Event</div>
            <div style="text-align:right;padding-right:24px;">Actual</div>
            <div style="text-align:right;padding-right:24px;">Forecast</div>
            <div style="text-align:right;padding-right:24px;">Previous</div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Each day ──────────────────────────────────────────────────────────────
    has_any = False
    for day in week_days:
        day_str  = day.isoformat()
        day_evts = events_by_day.get(day_str, [])
        is_today = (day == today)
        is_wknd  = day.weekday() >= 5

        today_badge = (
            '<span style="background:linear-gradient(135deg,#f97316,#ef4444);'
            'color:#fff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;'
            'letter-spacing:.5px;">TODAY</span>' if is_today else ""
        )
        count_label = f"{len(day_evts)} event{'s' if len(day_evts)!=1 else ''}" if day_evts else "No events"
        day_color   = "#2a2a2a" if is_wknd else "#111"

        st.markdown(
            f'<div class="day-header" style="background:{day_color};">'
            f'  <div class="day-num">{day.day:02d}</div>'
            f'  <div class="day-info">'
            f'    <div class="day-name">{day.strftime("%A, %B %Y")} {today_badge}</div>'
            f'    <div class="day-count">{count_label}</div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if not day_evts:
            st.markdown('<div class="empty-day">No events for this day.</div>', unsafe_allow_html=True)
            continue

        has_any   = True
        rows_html = []
        for ev in day_evts:
            impact   = (ev.get("impact_level") or "low").lower()
            currency = ev.get("currency", "")
            name     = ev.get("event_name", "")
            t        = ev.get("event_time") or ""
            raw_time = str(t)[:5] if t and len(str(t)) >= 5 else "All day"
            time_str = convert_time(raw_time, selected_tz) if raw_time != "All day" else "All day"

            actual_str   = _fmt_value(ev.get("actual_value"),   ev.get("actual_num"))
            forecast_str = _fmt_value(ev.get("forecast_value"), ev.get("forecast_num"))
            previous_str = _fmt_value(ev.get("previous_value"), ev.get("previous_num"))
            actual_cls   = _actual_class(ev.get("actual_num"), ev.get("forecast_num"), ev.get("previous_num"))

            _tc, _bb, row_bg, row_border = IMPACT_COLORS.get(impact, ("#6b7280", "#1e1e1e", "transparent", "#6b7280"))

            rows_html.append(
                f'<div class="cal-row" style="background:{row_bg};border-left:3px solid {row_border};">'
                f'  <div class="cal-cell time">{time_str}</div>'
                f'  <div class="cal-cell"><span class="currency-badge">{flag_img(currency)} {currency}</span></div>'
                f'  <div class="cal-cell">{_impact_html(impact)}</div>'
                f'  <div class="cal-cell event-name">{name}</div>'
                f'  <div class="cal-cell value {actual_cls}">{actual_str}</div>'
                f'  <div class="cal-cell value forecast">{forecast_str}</div>'
                f'  <div class="cal-cell value previous">{previous_str}</div>'
                f'</div>'
            )

        # Wrap rows trong scroll container
        st.markdown(
            '<div class="cal-table-wrapper">' + "".join(rows_html) + '</div>',
            unsafe_allow_html=True,
        )

    if not has_any:
        st.markdown(
            '<div class="no-events"><div style="font-size:48px;margin-bottom:16px;">📭</div>'
            '<p>No events found for this date range with current filters.</p></div>',
            unsafe_allow_html=True,
        )

with right_col:
    # ── Next High Impact events ───────────────────────────────────────────────
    from datetime import datetime, timezone as tz

    today_str = date.today().isoformat()
    upcoming_high = [
        ev for ev in events
        if ev.get("impact_level") == "high"
        and str(ev.get("event_date", ""))[:10] >= today_str
        and ev.get("actual_value") in (None, "", "—")
        and str(ev.get("actual_value") or "").strip() in ("", "None", "nan", "—")
    ]

    def _sort_key(ev):
        d = str(ev.get("event_date", ""))[:10]
        t = str(ev.get("event_time") or "23:59")[:5]
        return f"{d} {t}"
    upcoming_high = sorted(upcoming_high, key=_sort_key)[:8]

    items_html = ""
    prev_date  = None
    for ev in upcoming_high:
        ev_date     = str(ev.get("event_date", ""))[:10]
        ev_raw_time = str(ev.get("event_time") or "")[:5] or "All day"
        ev_time     = convert_time(ev_raw_time, selected_tz) if ev_raw_time != "All day" else "All day"
        currency    = ev.get("currency", "")
        name        = ev.get("event_name", "")
        code        = CURRENCY_COUNTRY.get(currency, "")
        flag_url    = f"https://flagcdn.com/w40/{code}.png" if code else ""
        flag_tag    = (
            f'<img src="{flag_url}" width="16" height="16" '
            f'style="border-radius:50%;object-fit:cover;vertical-align:middle;'
            f'border:1px solid rgba(255,255,255,0.15);margin-right:4px;" />'
            if flag_url else ""
        )

        if ev_date != prev_date:
            try:
                from datetime import date as _date
                label = _date.fromisoformat(ev_date).strftime("%a %b %d")
            except Exception:
                label = ev_date
            is_tod    = ev_date == today_str
            dot_color = "#f97316" if is_tod else "#444"
            items_html += (
                f'<div style="font-size:12px;font-weight:700;color:{dot_color};'
                f'letter-spacing:1px;text-transform:uppercase;'
                f'margin:10px 0 6px 0;padding-top:6px;border-top:1px solid #1e1e1e;">'
                f'{label}</div>'
            )
            prev_date = ev_date

        items_html += (
            f'<div style="display:flex;flex-direction:column;gap:2px;'
            f'padding:8px 10px;border-radius:8px;margin-bottom:4px;'
            f'background:rgba(239,68,68,0.05);border-left:2px solid #ef4444;">'
            f'  <div style="display:flex;align-items:center;gap:5px;">'
            f'    <span style="font-family:DM Mono,monospace;font-size:12px;color:#666;">{ev_time}</span>'
            f'    {flag_tag}'
            f'    <span style="font-size:12px;font-weight:700;color:#ef4444;">{currency}</span>'
            f'  </div>'
            f'  <div style="font-size:13px;color:#ccc;line-height:1.4;font-weight:600;">{name}</div>'
            f'</div>'
        )

    if not items_html:
        items_html = '<div style="font-size:13px;color:#444;font-style:italic;">No upcoming HIGH events</div>'

    st.markdown(
        f'''<div style="background:#0d0d0d;border:1px solid #1e1e1e;
                    border-radius:12px;padding:16px 14px;">
          <div style="font-size:13px;font-weight:700;letter-spacing:1.5px;
                      text-transform:uppercase;color:#ef4444;margin-bottom:12px;">
            🔴 Next High Impact
          </div>
          {items_html}
        </div>''',
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