import streamlit as st

from lib.supabase.connection import get_conn, get_session_and_user
from lib.supabase.jobs import fetch_all_jobs, delete_job
from lib.supabase.profile_recruiter import fetch_profile_recruiter_by_id
from lib.supabase.storage import delete_from_supabase
from modules.kelolaJob import manage_job

conn = get_conn()
session, user = get_session_and_user(conn)

st.title("Unggahan Pekerjaan")
st.text("Kelola lowongan anda.")
st.divider()

@st.dialog(title="Konfirmasi Hapus Pekerjaan", width="small")
def confirm_delete_job(job, document, bucket_name):
    st.warning("⚠️ Anda yakin ingin menghapus lowongan pekerjaan ini?")
    if st.button("Ya, Hapus Pekerjaan Ini", use_container_width=True):
        success_del_img, error_del_img = delete_from_supabase(conn, bucket_name, document)
        if success_del_img:
            st.success("✅ File berhasil dihapus dari Supabase Storage.")

            success_del_job, error_del_job = delete_job(conn, job.get("id"))
            if success_del_job:
                st.success("✅ Lowongan pekerjaan berhasil dihapus.")
            else:
                st.error(f"❌ Gagal menghapus lowongan pekerjaan: {error_del_job}")
        else:
            st.error(f"❌ Gagal menghapus file: {error_del_img}")

        st.rerun()


all_jobs = fetch_all_jobs(conn)
            
SUPABASE_URL = st.secrets["SUPABASE_URL"]
bucket_name = st.secrets["bucket_name_jobs"]

if not all_jobs:
    st.info("Belum ada lowongan pekerjaan yang tersedia saat ini. Silakan kembali lagi nanti.")
else:
    my_jobs = [job for job in all_jobs if job.get("recruiter_id") == user.user.id]
    search_term = st.text_input("🔍 Cari Pekerjaan", placeholder="Ketik posisi pekerjaan yang ingin Anda cari...")
    st.write("")
    filtered_jobs = []
    if search_term:
        filtered_jobs = [
            job for job in my_jobs 
            if search_term.lower() in job.get("position", "").lower()
        ]
    else:
        filtered_jobs = my_jobs

    if not filtered_jobs:
        st.warning(f"Tidak ada pekerjaan dengan posisi '{search_term}'.")
    else:


        for index, job in enumerate(filtered_jobs):
            with st.container(border=True):

                document = job.get("document")
                document_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{document}" if document else None

            
                position = job.get("position", "Posisi Tdk Tersedia")
                company_name = job.get("company_name", "Perusahaan Tdk Tersedia")
                st.subheader(f'{position} - {company_name}')

                type_job = job.get("type_job")
                location = job.get("location")

                st.text(f'{type_job} - {location}')

                openned = job.get("openned")
                if openned:
                    st.badge("Status: Dibuka", color="green")
                else:
                    st.badge("Status: Ditutup", color="red")


                data_recruiter, error = fetch_profile_recruiter_by_id(conn, job.get("recruiter_id"))

                st.divider()

                description = job.get("description")
                phone = job.get("phone", " ")
                email = job.get("email", "-")
                app_in_person = job.get("app_in_person")

                if st.button("Kelola Pekerjaan", type="primary", use_container_width=True, key=f"btn_kelola_{job.get('id')}"):
                    manage_job(conn, job, user)

                if st.button("Hapus Pekerjaan", type="secondary", use_container_width=True, key=f"btn_delete_{job.get('id')}"):
                    confirm_delete_job(job, document, bucket_name)
                    

                st.write("")



