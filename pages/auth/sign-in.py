import streamlit as st
from lib.supabase.connection import get_conn, get_session_and_user
from lib.supabase.profile import insert_profile_user
from lib.supabase.profile_recruiter import insert_profile_recruiter

st.set_page_config(page_title="Sign In", page_icon="🔑")
st.title("🔑 Sign In")

conn = get_conn()
session, user = get_session_and_user(conn)

if user and user.user:
    st.success(f"Sudah login sebagai **{user.user.email}**")
    st.page_link("pages/home.py", label="➡️ Ke Home", icon="🏠")
    st.stop()

with st.form("login_form", clear_on_submit=False):
    email = st.text_input("Email", placeholder="you@example.com")
    password = st.text_input("Password", type="password")
    
    st.divider()
    submitted = st.form_submit_button("Masuk", type="primary", width="stretch")

if submitted:
    if not email or not password:
        st.warning("Email dan password wajib diisi.")
    else:
        try:
            conn.auth.sign_in_with_password({"email": email, "password": password})

            session, user = get_session_and_user(conn)
            
            if user and user.user:
                role = user.user.user_metadata.get("role")
                if  role != "user" :
                    insert_profile_recruiter(conn, user)
                else:
                    insert_profile_user(conn, user)
            
            st.toast("Berhasil masuk.", icon="✅")
            st.rerun()
            
        except Exception as e:
            st.error(f"Gagal masuk: {e}")

st.caption("Belum punya akun?")
st.page_link("pages/auth/sign-up.py", label="Daftar di sini", icon="✍️")
