"""
components/ads.py

Nhúng quảng cáo Monetag vào Streamlit qua components.html().
Luôn load script thật — hoạt động trên cả localhost lẫn production.
"""

import streamlit.components.v1 as components

MONETAG_ID = "1c4779d5387629aee789c034faab22ef"


def render_banner_ad(
    width: int = 728,
    height: int = 90,
    ad_unit_id: str = "",
) -> None:
    """
    Hiển thị banner quảng cáo Monetag.

    Parameters
    ----------
    width      : Chiều rộng vùng chứa (px). Mặc định 728.
    height     : Chiều cao vùng chứa (px). Mặc định 90.
    ad_unit_id : Zone ID riêng (để trống = dùng MONETAG_ID mặc định).
    """
    zone_id = ad_unit_id or MONETAG_ID

    components.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta name="monetag" content="{zone_id}">
          <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ background: transparent; overflow: hidden; }}
            #ad-wrap {{
              width: 100%;
              max-width: {width}px;
              min-height: {height}px;
              margin: 0 auto;
              display: flex;
              align-items: center;
              justify-content: center;
            }}
          </style>
        </head>
        <body>
          <div id="ad-wrap">
            <script async data-cfasync="false"
              src="https://thubanoa.com/1?z={zone_id}">
            </script>
          </div>
        </body>
        </html>
        """,
        height=height + 10,
        scrolling=False,
    )