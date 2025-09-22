import streamlit as st
from st_supabase_connection import SupabaseConnection

def insert_courses(conn: SupabaseConnection, data: dict):
    try:
        conn.client.table("courses").insert(data).execute()
        return True, None
    except Exception as e:
        return False, e
    
def fetch_all_courses(conn: SupabaseConnection):
    try:
        response = conn.client.table("courses").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Gagal mengambil courses: {e}")
        return []

def update_courses(conn: SupabaseConnection, courses_id, data: dict):
    try:
        conn.client.table("courses").update(data).eq("id", courses_id).execute()
        return True, None
    except Exception as e:
        return False, e

def delete_courses(conn: SupabaseConnection, courses_id):
    try:
        conn.client.table("courses").delete().eq("id", courses_id).execute()
        return True, None
    except Exception as e:
        return False, e