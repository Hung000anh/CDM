import streamlit as st
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY


@st.cache_resource
def get_client() -> Client:
    """
    Trả về Supabase Client duy nhất (singleton).

    @st.cache_resource đảm bảo hàm chỉ chạy 1 lần;
    các lần gọi tiếp theo trả về object đã được cache.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise EnvironmentError(
            "Thiếu biến môi trường SUPABASE_URL hoặc SUPABASE_KEY. "
            "Hãy kiểm tra file .env hoặc Streamlit Secrets."
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)
