import streamlit as st
from st_supabase_connection import SupabaseConnection

def insert_profile_user(conn: SupabaseConnection, user):
    try:
        data = {
            "id": user.user.id,
            "name": user.user.user_metadata.get("display_name"),
            "phone": user.user.user_metadata.get("phone"),
            "email": user.user.email,
        }
        
        conn.table("profiles").upsert(data, on_conflict="id").execute()

        return True, None
    except Exception as e:
        return False, e