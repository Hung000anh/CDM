"""
utils/path_setup.py
────────────────────
Đảm bảo root project (thư mục CDM/) luôn nằm trong sys.path,
cho dù Streamlit chạy từ thư mục nào.

Import file này ở dòng ĐẦU TIÊN của app.py và tất cả pages/*.py:
    import utils.path_setup  # noqa: F401  (phải là dòng đầu)
"""

import sys
from pathlib import Path

# Tìm root = thư mục chứa file này (utils/) → lên 1 cấp = CDM/
ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))