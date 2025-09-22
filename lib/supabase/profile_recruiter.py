import streamlit as st
from st_supabase_connection import SupabaseConnection

def insert_profile_recruiter(conn: SupabaseConnection, user):
    try:
        data = {
            "id": user.user.id,
            "name": user.user.user_metadata.get("display_name"),
            "phone": user.user.user_metadata.get("phone"),
            "email": user.user.email,
            "company_name":user.user.user_metadata.get("company_name"),
            "company_address":user.user.user_metadata.get("company_address"),
            "company_desc":user.user.user_metadata.get("company_desc"),
            "position":user.user.user_metadata.get("position"),

        }
        
        conn.table("profiles_recruiter").upsert(data, on_conflict="id").execute()

        return True, None
    except Exception as e:
        return False, e
    
def fetch_profile_recruiter_by_id(conn: SupabaseConnection, user_id: str):
    try:
        response = conn.table("profiles_recruiter").select("*").eq("id", user_id).execute()
        if response.data:
            return response.data[0], None
        else:
            return None, None
            
    except Exception as e:
        st.error(f"Gagal mengambil profil: {e}")
        return None, e