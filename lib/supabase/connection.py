import streamlit as st
from st_supabase_connection import SupabaseConnection

@st.cache_resource
def get_conn():
    return st.connection("supabase", type=SupabaseConnection)

def get_session_and_user(conn):
    try:
        return conn.auth.get_session(), conn.auth.get_user()
    except Exception:
        return None, None