import streamlit as st
from st_supabase_connection import SupabaseConnection

def fetch_kata_bisindo(conn: SupabaseConnection):
    try:
        response = conn.client.table("kata_bisindo").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Gagal mengambil kata: {e}")
        return []