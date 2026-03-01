"""
components/ads.py

Quản lý quảng cáo Monetag.
- Localhost  → hiển thị placeholder (để test layout)
- Production → nhúng script Monetag thật
"""

import os
import socket
import streamlit.components.v1 as components

# ── Publisher ID Monetag của bạn ──────────────────────────────────────────────
MONETAG_ID = "1c4779d5387629aee789c034faab22ef"


def _is_localhost() -> bool:
    """Kiểm tra có đang chạy trên localhost không."""
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = "127.0.0.1"
    return ip.startswith("127.") or ip.startswith("192.168.") or hostname == "localhost"


def render_banner_ad(
    width: int = 728,
    height: int = 90,
    ad_unit_id: str = "",
) -> None:
    """
    Hiển thị banner quảng cáo Monetag.

    Parameters
    ----------
    width       : Chiều rộng banner (px). Mặc định 728 (leaderboard).
    height      : Chiều cao banner (px). Mặc định 90.
    ad_unit_id  : Zone ID lấy từ Monetag dashboard (để trống = dùng MONETAG_ID).
    """
    zone_id = ad_unit_id or MONETAG_ID

    # ── Môi trường PRODUCTION: nhúng script Monetag thật ─────────────────────
    if not _is_localhost():
        components.html(
            f"""
            <!DOCTYPE html>
            <html>
            <head>
              <style>
                body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
                #ad-wrap {{
                  width: {width}px;
                  height: {height}px;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  margin: 0 auto;
                }}
              </style>
            </head>
            <body>
              <div id="ad-wrap">
                <script async data-cfasync="false"
                  src="//thubanoa.com/1?z={zone_id}">
                </script>
              </div>
            </body>
            </html>
            """,
            height=height + 10,
            scrolling=False,
        )

    # ── Môi trường LOCALHOST: hiển thị placeholder ────────────────────────────
    else:
        components.html(
            f"""
            <!DOCTYPE html>
            <html>
            <head>
              <style>
                body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
                .ad-placeholder {{
                  width: {width}px;
                  height: {height}px;
                  margin: 0 auto;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  background: repeating-linear-gradient(
                    45deg,
                    #1a1a1a,
                    #1a1a1a 10px,
                    #222 10px,
                    #222 20px
                  );
                  border: 1px dashed #444;
                  border-radius: 6px;
                  box-sizing: border-box;
                  gap: 10px;
                  font-family: system-ui, sans-serif;
                }}
                .ad-placeholder span {{
                  color: #666;
                  font-size: 12px;
                  letter-spacing: 1px;
                  text-transform: uppercase;
                  font-weight: 600;
                  white-space: nowrap;
                }}
                .ad-placeholder code {{
                  color: #f97316;
                  font-size: 11px;
                  background: rgba(249,115,22,0.1);
                  border: 1px solid rgba(249,115,22,0.25);
                  border-radius: 4px;
                  padding: 2px 6px;
                  font-family: monospace;
                }}
              </style>
            </head>
            <body>
              <div class="ad-placeholder">
                <span>📢 Ad Banner {width}×{height}</span>
                <code>Monetag – localhost preview</code>
              </div>
            </body>
            </html>
            """,
            height=height + 10,
            scrolling=False,
        )