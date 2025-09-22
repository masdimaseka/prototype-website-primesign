import streamlit as st
from st_supabase_connection import SupabaseConnection

def insert_job(conn: SupabaseConnection, data: dict):
    try:
        conn.client.table("jobs").insert(data).execute()
        return True, None
    except Exception as e:
        return False, e
    
def fetch_all_jobs(conn: SupabaseConnection):
    try:
        response = conn.client.table("jobs").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Gagal mengambil riwayat: {e}")
        return []

def update_job(conn: SupabaseConnection, job_id, data: dict):
    try:
        conn.client.table("jobs").update(data).eq("id", job_id).execute()
        return True, None
    except Exception as e:
        return False, e

def delete_job(conn: SupabaseConnection, job_id):
    try:
        conn.client.table("jobs").delete().eq("id", job_id).execute()
        return True, None
    except Exception as e:
        return False, e