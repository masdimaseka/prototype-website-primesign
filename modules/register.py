import streamlit as st
from st_supabase_connection import SupabaseConnection

def register_user(conn: SupabaseConnection, r_email, r_pass, r_pass2, r_display_name, r_phone ):
    if not r_email or not r_pass or not r_pass2 or not r_display_name or not r_phone:
        st.warning("Semua kolom wajib diisi.")
    elif r_pass != r_pass2:
        st.warning("Konfirmasi password tidak cocok.")
    elif len(r_pass) < 6:
        st.warning("Password minimal 6 karakter.")
    else:
        try:
            conn.auth.sign_up({
                "email": r_email,
                "password": r_pass,
                "options": {
                    "data": {
                        "display_name": r_display_name,
                        "phone": r_phone,
                        "role": "user"
                    }
                }
            })

        except Exception as e:
            st.error(f"Gagal daftar: {e}")
            return
        


def register_recruiter(conn: SupabaseConnection, r_company_name, r_company_add, r_company_desc,  r_email, r_pass, r_pass2, r_display_name, r_phone, r_company_u_poss):
    if not r_email or not r_pass or not r_pass2 or not r_display_name or not r_phone or not r_company_name or not r_company_add or not r_company_desc or not r_company_u_poss:
        st.warning("Semua kolom wajib diisi.")
    elif r_pass != r_pass2:
        st.warning("Konfirmasi password tidak cocok.")
    elif len(r_pass) < 6:
        st.warning("Password minimal 6 karakter.")
    else:
        try:
            conn.auth.sign_up({
                "email": r_email,
                "password": r_pass,
                "options": {
                    "data": {
                        "display_name": r_display_name,
                        "phone": r_phone,
                        "company_name": r_company_name,
                        "company_address": r_company_add,
                        "company_desc": r_company_desc,
                        "position": r_company_u_poss,
                        "role": "recruiter"
                    }
                }
            })

        except Exception as e:
            st.error(f"Gagal daftar: {e}")
            return
        
