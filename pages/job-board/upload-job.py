import streamlit as st
import uuid

from datetime import datetime
from lib.supabase.connection import get_conn, get_session_and_user
from lib.supabase.jobs import insert_job
from lib.supabase.storage import upload_to_supabase

st.set_page_config(page_title="Form Unggah Pekerjaan", page_icon="📄")

conn = get_conn()
session, user = get_session_and_user(conn)

if not user or not user.user:
    st.warning("Anda harus login untuk mengakses halaman ini.")
    st.stop()

st.title("Unggah Lowongan Pekerjaan Baru")
st.text("Silakan isi detail pekerjaan di bawah ini dan unggah dokumen yang relevan.")

with st.form("job_upload_form", clear_on_submit=False):

    st.subheader("Unggah Dokumen")
    uploaded_file = st.file_uploader(
        "Unggah poster mengenai lowongan pekejaan",
        type=["png", "jpg", "jpeg"]
    )

    st.divider()

    st.subheader("Detail Pekerjaan")

    col1, col2 = st.columns(2)

    with col1:
        job_title = st.text_input("Nama Posisi/Jabatan*", placeholder="Contoh: Software Engineer")
        company_name = st.text_input("Nama Perusahaan*", placeholder="Contoh: PT Teknologi Maju")
        
    with col2:
        location = st.text_input("Lokasi*", placeholder="Contoh: Jakarta, Indonesia")
        job_type = st.selectbox(
            "Tipe Pekerjaan*",
            ("Penuh Waktu (Full-time)", "Paruh Waktu (Part-time)", "Kontrak", "Magang (Internship)")
        )


    job_description = st.text_area(
        "Deskripsi Pekerjaan*",
        placeholder="Jelaskan tanggung jawab utama, kualifikasi yang dibutuhkan, dan informasi lain mengenai pekerjaan ini.",
        height=200
    )

    st.divider()

    st.subheader("Kirim Lamaran")

    whatsapp_number = None
    email_address = None

    email_address = st.text_input(
        "Alamat Email*", 
        placeholder="Contoh: hrd@perusahaan.com"
    )
    whatsapp_number = st.text_input(
        "Nomor WhatsApp", 
        placeholder="Contoh: 081234567890"
    )

    apply_in_person = st.checkbox("Datang Langsung ke kantor")

    st.divider()

    submitted = st.form_submit_button("Unggah Pekerjaan", type="primary", width="stretch")

if submitted:
    if not job_title or not company_name or not location or not job_description or not job_type or not email_address:
        st.warning("Mohon lengkapi semua kolom yang wajib diisi.")
    else:
        original_filename = uploaded_file.name.rsplit('.', 1)[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4()).split('-')[0]

        doc_file_name = f"{original_filename}_{timestamp}_{unique_id}_caption.png"
        supabase_image_path = f"{user.user.id}/{doc_file_name}"

        file_bytes = uploaded_file.getvalue()
        content_type = uploaded_file.type 

        image_upload_success, image_upload_error = upload_to_supabase(
            conn, 
            file_bytes, 
            "jobs", 
            supabase_image_path, 
            content_type
        )

        if image_upload_success:
            st.toast("📤 Berhasil mengunggah file ke Storage!")
            data = {
                "recruiter_id": user.user.id,
                "position": job_title,
                "company_name": company_name,
                "location": location,
                "type_job": job_type,
                "description": job_description,
                "phone": whatsapp_number,
                "email": email_address,
                "app_in_person": apply_in_person,
                "openned": True,
                "document": supabase_image_path
            }
            
            insert_success, insert_error = insert_job(conn, data)
            if insert_success:
                st.success("🎉 Lowongan pekerjaan berhasil diunggah!")
                st.switch_page("pages/job-board/list-job.py")
                st.rerun()
            else:
                st.error(f"Gagal menyimpan riwayat: {insert_error}")

        else:
            st.error(f"Gagal mengunggah file: {image_upload_error}")
        