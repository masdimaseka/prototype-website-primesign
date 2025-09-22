import streamlit as st
from lib.supabase.connection import get_conn, get_session_and_user
from modules.register import register_user, register_recruiter

st.set_page_config(page_title="Sign Up", page_icon="📝")
st.title("📝 Sign Up")

conn = get_conn()
session, user = get_session_and_user(conn)

if user and user.user:
    st.success(f"Sudah login sebagai **{user.user.email}**")
    st.page_link("pages/home.py", label="➡️ Ke Home", icon="🏠")
    st.stop()


tab1_r_user, tab2_r_recruiter = st.tabs(["Daftar sebagai user", "Daftar sebagai recruiter"])

with tab1_r_user:
    with st.form("register_user_form", clear_on_submit=False):

        col_name, col_phone = st.columns(2)
        with col_name:
            r_display_name = st.text_input("Nama", placeholder="Nama Lengkap Anda")
        with col_phone:
            r_phone = st.text_input("No Telp", placeholder="08...")

        r_email = st.text_input("Email", placeholder="you@example.com")

        col1, col2 = st.columns(2)
        with col1:
            r_pass = st.text_input("Password", type="password")
        with col2:
            r_pass2 = st.text_input("Konfirmasi Password", type="password")
        
        st.divider()
        submitted_user = st.form_submit_button("Daftar", type="primary", width="stretch")

    if submitted_user:
        register_user(conn, r_email, r_pass, r_pass2, r_display_name, r_phone)

with tab2_r_recruiter:
    with st.form("register_recruiter_form", clear_on_submit=False):

        r_company_name = st.text_input("Nama perusahaan", placeholder="PT. ABC...")
        r_company_add = st.text_input("Lokasi perusahaan", placeholder="Jl. ABC, Kota ABC, Provinsi ABC")
        r_company_desc = st.text_area("Deskripsi tentang perusahaan", placeholder="PT ABC merupakan")
        st.divider()

        col_name, col_phone = st.columns(2)
        with col_name:
            r_display_name = st.text_input("Nama", placeholder="Nama Lengkap Anda")
        with col_phone:
            r_phone = st.text_input("No Telp", placeholder="08...")

        r_email = st.text_input("Email", placeholder="you@example.com")

        col1, col2 = st.columns(2)
        with col1:
            r_pass = st.text_input("Password", type="password")
        with col2:
            r_pass2 = st.text_input("Konfirmasi Password", type="password")
        
        r_company_u_poss = st.text_input("Jabatan di perusahaan", placeholder="HRD atau yang lain")
        
        st.divider()
        submitted_recruiter  = st.form_submit_button("Daftar", type="primary", width="stretch")

    if submitted_recruiter :
        register_recruiter(conn, r_company_name, r_company_add, r_company_desc,  r_email, r_pass, r_pass2, r_display_name, r_phone, r_company_u_poss)

st.divider()

st.caption("Sudah punya akun?")
st.page_link("pages/auth/sign-in.py", label="Masuk di sini", icon="🔑")