import streamlit as st
import uuid

from datetime import datetime
from lib.supabase.jobs import update_job
from lib.supabase.storage import delete_from_supabase, upload_to_supabase

@st.dialog(title="Detail Pekerjaan", width="medium")
def show_detail_job(document_url, position, company_name, type_job, location, description, data_recruiter, phone, email, app_in_person):
    st.image(document_url)
    st.header(f'{position} - {company_name}')
    with st.container(horizontal=True):
        st.badge(type_job, color="blue")
        st.badge(location, color="green")
    st.markdown(f'Posted by **{data_recruiter.get("name")}**, **{data_recruiter.get("position")}**, **{data_recruiter.get("company_name")}**')
    
    st.divider()
    st.header("Deskripsi Pekerjaan")
    st.text(description)

    st.divider()
    st.header("Kirim Lamaran")
    with st.container(border=True):
        st.text(f'Email : {email}')

        if phone: 
            st.text(f'Whatsapp : {phone}')

        if app_in_person == True:
            st.text(f'Kirim ke : {location}')

@st.dialog(title="Kelola Pekerjaan", width="medium")
def manage_job(conn, job, user):
    st.subheader("📝 Ubah Detail Pekerjaan")

    if 'processing' not in st.session_state:
        st.session_state.processing = False

    with st.form("edit_job_form"):
        st.subheader("Ganti Dokumen (Opsional)")
        uploaded_file = st.file_uploader(
            "Unggah poster baru jika ingin mengganti yang lama.",
            type=["png", "jpg", "jpeg"]
        )

        col1, col2 = st.columns(2)
        with col1:
            new_position = st.text_input("Nama Posisi/Jabatan", value=job.get("position", ""))
            new_company_name = st.text_input("Nama Perusahaan", value=job.get("company_name", ""))
        
        with col2:
            new_location = st.text_input("Lokasi", value=job.get("location", ""))
            
            job_type_options = ["Penuh Waktu (Full-time)", "Paruh Waktu (Part-time)", "Kontrak", "Magang (Internship)"]
            try:
                current_type_index = job_type_options.index(job.get("type_job"))
            except (ValueError, TypeError):
                current_type_index = 0 
            
            new_type_job = st.selectbox("Tipe Pekerjaan", options=job_type_options, index=current_type_index)

        new_description = st.text_area("Deskripsi Pekerjaan", value=job.get("description", ""), height=250)

        st.divider()
        st.subheader("Kirim Lamaran")
        new_email = st.text_input("Email", value=job.get("email", ""))
        new_phone = st.text_input("Nomor WhatsApp (Opsional)", value=job.get("phone", ""))
        new_app_in_person = st.checkbox("Datang Langsung ke Kantor", value=job.get("app_in_person", False))
        
        st.divider()

        st.subheader("Status Lowongan")
        is_open = job.get("openned", True)
        new_openned = st.checkbox("Dibuka", value=is_open)

        st.divider()

        button_text = "⏳ Sedang Memproses..." if st.session_state.processing else "✅ Simpan Perubahan"
        submitted = st.form_submit_button(
            button_text,
            type="primary",
            use_container_width=True,
            disabled=st.session_state.processing
        )

        if submitted:
            st.session_state.processing = True
            
            try:
                data_to_update = {
                    "position": new_position,
                    "company_name": new_company_name,
                    "location": new_location,
                    "type_job": new_type_job,
                    "description": new_description,
                    "email": new_email,
                    "phone": new_phone,
                    "app_in_person": new_app_in_person,
                    "openned": new_openned
                }

                if uploaded_file:
                    if job.get("document"):
                        success_del, err_del = delete_from_supabase(conn, "jobs", job.get("document"))
                        if not success_del:
                            st.error(f"❌ Gagal menghapus file lama: {err_del}")

                    original_filename = uploaded_file.name.rsplit('.', 1)[0]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_id = str(uuid.uuid4()).split('-')[0]
                    doc_file_name = f"{original_filename}_{timestamp}_{unique_id}.png"
                    supabase_image_path = f"{user.user.id}/{doc_file_name}"
                    
                    file_bytes = uploaded_file.getvalue()
                    content_type = uploaded_file.type

                    success_upload, err_upload = upload_to_supabase(
                        conn, file_bytes, "jobs", supabase_image_path, content_type
                    )

                    if not success_upload:
                        st.error(f"❌ Gagal mengunggah file baru: {err_upload}")
                        return 
                    
                    data_to_update["document"] = supabase_image_path

                update_success, update_error = update_job(conn, job.get("id"), data_to_update)

                if update_success:
                    st.success("🎉 Perubahan berhasil disimpan!")
                    del st.session_state.processing 
                    st.rerun()
                else:
                    st.error(f"Gagal menyimpan perubahan ke database: {update_error}")

            finally:
                st.session_state.processing = False

                

           
           