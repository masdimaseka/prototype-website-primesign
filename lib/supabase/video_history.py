import streamlit as st
from st_supabase_connection import SupabaseConnection

def insert_detection_video_history(conn: SupabaseConnection, data: dict):
    try:
        conn.client.table("detection_video_history").insert(data).execute()
        return True, None
    except Exception as e:
        return False, e

def fetch_detection_video_history(conn: SupabaseConnection):
    try:
        response = conn.client.table("detection_video_history").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Gagal mengambil riwayat: {e}")
        return []