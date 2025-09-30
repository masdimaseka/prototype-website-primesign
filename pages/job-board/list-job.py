import streamlit as st

from lib.supabase.connection import get_conn, get_session_and_user
from lib.supabase.jobs import fetch_all_jobs
from lib.supabase.profile_recruiter import fetch_profile_recruiter_by_id
from lib.supabase.profile import fetch_profile_by_id
from modules.kelolaJob import show_detail_job

conn = get_conn()
session, user = get_session_and_user(conn)

st.title("Job Board")
st.text("Temukan peluang karir terbaru yang tersedia untuk Anda.")
st.divider()

@st.dialog(title="Tidak dapat diakses", width="small")
def no_access_dialog():
    st.warning("Anda harus masuk untuk mengakses halaman ini.")

all_jobs = fetch_all_jobs(conn)
            
SUPABASE_URL = st.secrets["SUPABASE_URL"]
bucket_name = st.secrets["bucket_name_jobs"]

if not all_jobs:
    st.info("Belum ada lowongan pekerjaan yang tersedia saat ini. Silakan kembali lagi nanti.")
else:
    open_jobs = [job for job in all_jobs if job.get("openned") is True]
    search_term = st.text_input("🔍 Cari Pekerjaan", placeholder="Ketik posisi pekerjaan yang ingin Anda cari...")
    st.write("")
    filtered_jobs = []
    if search_term:
        filtered_jobs = [
            job for job in open_jobs 
            if search_term.lower() in job.get("position", "").lower()
        ]
    else:
        filtered_jobs = open_jobs

    if not filtered_jobs:
        st.warning(f"Tidak ada pekerjaan dengan posisi '{search_term}'.")
    else:

        col1, col2 = st.columns(2, gap="large")

        for index, job in enumerate(filtered_jobs):
            
            if index % 2 == 0:
                with col1:
                    with st.container(border=True):
                        document = job.get("document")
                        document_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{document}" if document else None
                        
                        if document_url:
                            st.image(document_url)
                        
                        position = job.get("position", "Posisi Tdk Tersedia")
                        company_name = job.get("company_name", "Perusahaan Tdk Tersedia")
                        st.subheader(f'{position}') 
                        st.write(f"**{company_name}**") 

                        type_job = job.get("type_job")
                        location = job.get("location")
                        
                        with st.container(horizontal=True):
                            st.badge(type_job, color="blue")
                            st.badge(location, color="green")

                        data_recruiter, error = fetch_profile_recruiter_by_id(conn, job.get("recruiter_id"))
                        if data_recruiter is None:
                            data_recruiter, error = fetch_profile_by_id(conn, job.get("recruiter_id"))

                        st.markdown(f'Posted by **{data_recruiter.get("name")}**, **{data_recruiter.get("position")}**, **{data_recruiter.get("company_name")}**')

                        st.divider()

                        description = job.get("description")
                        phone = job.get("phone", " ")
                        email = job.get("email", "-")
                        app_in_person = job.get("app_in_person")

                        if st.button("Lihat Pekerjaan", type="secondary", use_container_width=True, key=f"btn_{job.get('id')}"):
                            if not user:
                                    no_access_dialog()
                            else:
                                show_detail_job(document_url, position, company_name, type_job, location, description, data_recruiter, phone, email, app_in_person)
                
                    st.write("") 

            else:
                with col2:
                    with st.container(border=True):
                        document = job.get("document")
                        document_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{document}" if document else None
                        
                        if document_url:
                            st.image(document_url)
                        
                        position = job.get("position", "Posisi Tdk Tersedia")
                        company_name = job.get("company_name", "Perusahaan Tdk Tersedia")
                        st.subheader(f'{position}')
                        st.write(f"**{company_name}**")

                        type_job = job.get("type_job")
                        location = job.get("location")
                        
                        with st.container(horizontal=True):
                            st.badge(type_job, color="blue")
                            st.badge(location, color="green")

                        data_recruiter, error = fetch_profile_recruiter_by_id(conn, job.get("recruiter_id"))
                        if data_recruiter is None:
                            data_recruiter, error = fetch_profile_by_id(conn, job.get("recruiter_id"))

                        st.markdown(f'Posted by **{data_recruiter.get("name")}**, **{data_recruiter.get("position")}**, **{data_recruiter.get("company_name")}**')

                        st.divider()

                        description = job.get("description")
                        phone = job.get("phone", " ")
                        email = job.get("email", "-")
                        app_in_person = job.get("app_in_person")

                        if st.button("Lihat Pekerjaan", type="secondary", use_container_width=True, key=f"btn_{job.get('id')}"):
                                if not user:
                                    no_access_dialog()
                                else:
                                    show_detail_job(document_url, position, company_name, type_job, location, description, data_recruiter, phone, email, app_in_person)
                    
                    st.write("")



