import streamlit as st
from lib.supabase.connection import get_conn, get_session_and_user
from datetime import datetime


st.set_page_config(page_title="Profile", page_icon="👤")
st.title("👤 Profil Pengguna")

conn = get_conn()
session, user = get_session_and_user(conn)

if user and user.user:

    st.subheader("Informasi Akun Anda")

    display_name = user.user.user_metadata.get("display_name", "-")
    phone = user.user.user_metadata.get("phone", "-")
    email = user.user.user_metadata.get("email", "-")
    
    created_at_value = user.user.created_at
    bergabung_sejak = "-" 

    if isinstance(created_at_value, datetime):
        bergabung_sejak = created_at_value.strftime("%d %B %Y")
    elif isinstance(created_at_value, str):
        try:
            bergabung_sejak = datetime.fromisoformat(created_at_value.replace("Z", "+00:00")).strftime("%d %B %Y")
        except ValueError:
            bergabung_sejak = "-" 
            
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Display Name", value=display_name, disabled=True)
        st.text_input("Email", value=email, disabled=True)
    with col2:
        st.text_input("Phone", value=phone, disabled=True)
        st.text_input("Bergabung Sejak", value=bergabung_sejak, disabled=True)

    st.divider()

    if st.button("Logout", type="secondary"):
        try:
            conn.auth.sign_out()
            st.rerun()
        except Exception as e:
            st.error(f"Terjadi masalah saat logout: {e}")

else:
    st.warning("Anda belum login.")
    st.write("Silakan masuk untuk melihat halaman profil Anda.")
    st.page_link("pages/auth/sign-in.py", label="➡️ Ke Halaman Login", icon="🔑")