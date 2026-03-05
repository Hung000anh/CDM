"""
pages/02_📰_News.py
────────────────────
News page với tính năng:
  - Tìm kiếm theo từ khoá (title + description)
  - Lọc theo date range
  - Lọc theo quốc gia
  - Phân trang (load more)
"""

import utils.path_setup  # noqa: F401
import sys
from pathlib import Path
from datetime import date, timedelta

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
from core import get_client, cache_short
from data.queries.symbols import get_countries

SUPPORT_URL  = "https://omg10.com/4/10659204"
PAGE_SIZE    = 18   # số bài mỗi lần load

st.set_page_config(
    page_title="CDM | News",
    page_icon="🫓",
    layout="wide",
)

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=DM+Sans:ital,wght@0,400;0,500;1,400&display=swap');

    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
    }}

    .block-container {{ padding-top: 2rem; }}

    /* ── FAB ── */
    .support-fab {{
        position: fixed; bottom: 60px; right: 24px; z-index: 99999;
        background: linear-gradient(135deg, #f97316, #ef4444);
        color: #ffffff !important; font-size: 15px; font-weight: 700;
        padding: 13px 28px; border-radius: 24px; text-decoration: none !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.45);
        transition: opacity .2s, transform .2s;
    }}
    .support-fab:hover {{ opacity: 0.88; transform: translateY(-2px); }}

    /* ── News card ── */
    .news-card {{
        background: #161616;
        border: 1px solid #242424;
        border-radius: 16px;
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;
        transition: border-color .2s, transform .2s, box-shadow .2s;
        cursor: pointer;
    }}
    .news-card:hover {{
        border-color: #f97316;
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(249,115,22,0.15);
    }}
    .news-card-img {{
        width: 100%; aspect-ratio: 16/9; object-fit: cover;
        display: block;
    }}
    .news-card-img-placeholder {{
        width: 100%; aspect-ratio: 16/9;
        background: linear-gradient(135deg, #1e1e1e, #2a2a2a);
        display: flex; align-items: center; justify-content: center;
        font-size: 32px; color: #444;
    }}
    .news-card-body {{
        padding: 16px 18px 20px 18px;
        flex: 1; display: flex; flex-direction: column; gap: 10px;
    }}
    .news-card-meta {{
        display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
    }}
    .news-badge {{
        background: rgba(249,115,22,0.12);
        border: 1px solid rgba(249,115,22,0.3);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 11px; font-weight: 700;
        color: #f97316; letter-spacing: .5px;
        text-transform: uppercase;
    }}
    .news-date {{
        font-size: 11.5px; color: #555;
    }}
    .news-card-title {{
        font-family: 'Sora', sans-serif;
        font-size: 14.5px; font-weight: 700;
        color: #f0f0f0; line-height: 1.5;
        margin: 0;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}
    .news-card-desc {{
        font-size: 12.5px; color: #777;
        line-height: 1.65; margin: 0;
        flex: 1;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}
    .news-card-source {{
        font-size: 11.5px; color: #444;
        margin-top: auto; padding-top: 8px;
        border-top: 1px solid #222;
    }}
    .news-card-link {{
        text-decoration: none !important;
        color: inherit !important;
        display: block; height: 100%;
    }}

    /* ── Results bar ── */
    .results-bar {{
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 8px;
    }}
    .results-count {{
        font-size: 13px; color: #666;
    }}

    /* ── Empty state ── */
    .empty-state {{
        text-align: center; padding: 80px 0; color: #444;
    }}
    .empty-state .icon {{ font-size: 52px; margin-bottom: 16px; }}
    .empty-state p {{ font-size: 14px; }}

    /* Date input – align vertically with search bar */
    div[data-testid="stDateInput"] {{
        margin-top: 0 !important;
    }}
    div[data-testid="stDateInput"] input {{
        font-size: 13px !important;
    }}
    </style>
    <a class="support-fab" href="{SUPPORT_URL}" target="_blank">🙏 Click ads to Support Me</a>
    """,
    unsafe_allow_html=True,
)


# ── Data layer ────────────────────────────────────────────────────────────────
@cache_short
def fetch_news(
    keyword: str,
    country_ids: tuple,
    date_from: str,
    date_to: str,
    offset: int,
    limit: int,
) -> list[dict]:
    client = get_client()
    q = (
        client.table("news_articles")
        .select("id, title, description, url, image_url, published_at, source_domain, country_id")
        .order("published_at", desc=True)
        .range(offset, offset + limit - 1)
    )

    if keyword.strip():
        q = q.ilike("title", f"%{keyword.strip()}%")

    if country_ids:
        q = q.in_("country_id", list(country_ids))

    if date_from:
        q = q.gte("published_at", f"{date_from}T00:00:00+00:00")

    if date_to:
        q = q.lte("published_at", f"{date_to}T23:59:59+00:00")

    res = q.execute()
    return res.data or []


@cache_short
def count_news(
    keyword: str,
    country_ids: tuple,
    date_from: str,
    date_to: str,
) -> int:
    client = get_client()
    q = (
        client.table("news_articles")
        .select("id", count="exact")
        .order("published_at", desc=True)
    )
    if keyword.strip():
        q = q.ilike("title", f"%{keyword.strip()}%")
    if country_ids:
        q = q.in_("country_id", list(country_ids))
    if date_from:
        q = q.gte("published_at", f"{date_from}T00:00:00+00:00")
    if date_to:
        q = q.lte("published_at", f"{date_to}T23:59:59+00:00")

    res = q.execute()
    return res.count or 0


# ── Sidebar ───────────────────────────────────────────────────────────────────
BMC_URL = "https://buymeacoffee.com/hung000anh"
GMAIL   = "hung000anh@gmail.com"

today        = date.today()
default_from = today - timedelta(days=30)

with st.sidebar:

    # ── Country filter ────────────────────────────────────────────────────────
    countries = get_countries()
    country_id_to_name = {c["id"]: c["name"] for c in countries}

    st.markdown("**🌍 Country**")

    with st.expander("Select country", expanded=True):
        selected_country_name = st.radio(
            "Select country",
            options=[c["name"] for c in countries],
            key="news_radio_country",
            label_visibility="collapsed",
        )

    selected_country = next((c for c in countries if c["name"] == selected_country_name), None)
    selected_cids    = (selected_country["id"],) if selected_country else ()
    is_all_countries = False

    st.divider()

    # ── Search ────────────────────────────────────────────────────────────────
    keyword = st.text_input("Search", placeholder="Search by title…", key="news_search_kw")

    st.divider()

    # ── Date range ────────────────────────────────────────────────────────────
    d_from = st.date_input("From", value=default_from, key="news_date_from")
    d_to   = st.date_input("To",   value=today,        key="news_date_to")

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


# ── Main content ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="padding: 24px 0 8px 0;">
        <div style="font-size:11px;color:#f97316;font-weight:700;
                    letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">
            Market Intelligence
        </div>
        <h1 style="font-family:'Sora',sans-serif;font-size:38px;
                   font-weight:900;margin:0 0 6px 0;line-height:1.1;">
            📰 News Feed
        </h1>
        <p style="font-size:14px;color:#666;margin:0;">
            Financial & economic news across G8 markets
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Resolve filter values ─────────────────────────────────────────────────────
date_from_str = d_from.isoformat() if d_from else ""
date_to_str   = d_to.isoformat()   if d_to   else ""
filter_cids   = () if is_all_countries else selected_cids

# validate date order
if d_from and d_to and d_from > d_to:
    st.warning("⚠️ 'From' date must be before or equal to 'To' date.")
    st.stop()

# ── Load-more state ───────────────────────────────────────────────────────────
filter_sig = (keyword, filter_cids, date_from_str, date_to_str)
if st.session_state.get("_last_filter") != filter_sig:
    st.session_state["_last_filter"]  = filter_sig
    st.session_state["news_offset"]   = 0

offset = st.session_state.get("news_offset", 0)

# ── Fetch data ────────────────────────────────────────────────────────────────
with st.spinner("Loading news…"):
    articles = fetch_news(
        keyword=keyword,
        country_ids=filter_cids,
        date_from=date_from_str,
        date_to=date_to_str,
        offset=0,
        limit=offset + PAGE_SIZE,
    )
    total = count_news(keyword, filter_cids, date_from_str, date_to_str)

# ── Results bar ───────────────────────────────────────────────────────────────
shown = len(articles)
kw_display = f' for "<b>{keyword}</b>"' if keyword.strip() else ""
st.markdown(
    f'<div class="results-bar">'
    f'<span class="results-count">Showing <b>{shown}</b> of <b>{total}</b> articles{kw_display}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Render cards ──────────────────────────────────────────────────────────────
COLS = 3

if not articles:
    st.markdown(
        """
        <div class="empty-state">
            <div class="icon">🔍</div>
            <p>No articles found matching your filters.<br>Try adjusting your search or date range.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for row_start in range(0, len(articles), COLS):
        row_articles = articles[row_start : row_start + COLS]
        cols = st.columns(COLS)
        for col, art in zip(cols, row_articles):
            with col:
                img_tag = (
                    f'<img class="news-card-img" src="{art["image_url"]}" '
                    f'onerror="this.style.display=\'none\';this.nextSibling.style.display=\'flex\';" />'
                    f'<div class="news-card-img-placeholder" style="display:none;">📰</div>'
                    if art.get("image_url")
                    else '<div class="news-card-img-placeholder">📰</div>'
                )

                pub = art.get("published_at", "")
                try:
                    from datetime import datetime, timezone
                    dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                    date_str = dt.strftime("%b %d, %Y · %H:%M")
                except Exception:
                    date_str = pub[:10] if pub else ""

                country_name = country_id_to_name.get(art.get("country_id", ""), "")
                desc         = art.get("description") or ""
                title        = art.get("title", "No title")
                source       = art.get("source_domain", "")
                url          = art.get("url", "#")

                badge_html = (
                    f'<span class="news-badge">{country_name}</span>'
                    if country_name else ""
                )

                st.markdown(
                    f"""
                    <a class="news-card-link" href="{url}" target="_blank" rel="noopener noreferrer">
                      <div class="news-card">
                        {img_tag}
                        <div class="news-card-body">
                          <div class="news-card-meta">
                            {badge_html}
                            <span class="news-date">{date_str}</span>
                          </div>
                          <p class="news-card-title">{title}</p>
                          {"<p class='news-card-desc'>" + desc + "</p>" if desc else ""}
                          <div class="news-card-source">🔗 {source}</div>
                        </div>
                      </div>
                    </a>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)

# ── Load more button ──────────────────────────────────────────────────────────
if shown < total:
    remaining = total - shown
    st.markdown("<br>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([3, 2, 3])
    with btn_col:
        if st.button(
            f"Load more  ({remaining} remaining)",
            use_container_width=True,
            key="news_load_more",
        ):
            st.session_state["news_offset"] = offset + PAGE_SIZE
            st.rerun()
else:
    if articles:
        st.markdown(
            "<p style='text-align:center;color:#444;font-size:12px;padding:16px 0 8px;'>"
            "— You've reached the end —"
            "</p>",
            unsafe_allow_html=True,
        )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    f"<center style='color:#555;padding:12px 0 24px 0;font-size:13px;'>"
    f"CDM © 2026 &nbsp;·&nbsp; Built with Streamlit &nbsp;·&nbsp; "
    f"<a href='{SUPPORT_URL}' style='color:#f97316;text-decoration:none;'>🙏 Click ads to Support Me</a>"
    f"</center>",
    unsafe_allow_html=True,
)