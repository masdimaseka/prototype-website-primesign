import streamlit as st
import uuid

from datetime import datetime
from lib.supabase.connection import get_conn, get_session_and_user
from lib.supabase.courses import insert_courses
from lib.supabase.storage import upload_to_supabase

st.set_page_config(page_title="Form Unggah Pelatihan", page_icon="📄")

conn = get_conn()
session, user = get_session_and_user(conn)

if not user or not user.user:
    st.warning("Anda harus login untuk mengakses halaman ini.")
    st.stop()

st.title("Unggah Video Pelatihan Baru")
st.text("Silakan isi detail pealtihan di bawah ini.")

with st.form("job_upload_form", clear_on_submit=False):

    st.subheader("Unggah Thumbnail Pelatihan")
    uploaded_file = st.file_uploader(
        "Unggah dengan ukuran 1920x1080 px*",
        type=["png", "jpg", "jpeg"]
    )

    st.divider()

    st.subheader("Detail Pelatihan")

    title = st.text_input("Judul Pelatihan*", placeholder="Contoh: Belajar Pemrograman Python")
    description = st.text_area(
        "Deskripsi Pelatihan*",
        placeholder="Jelaskan tanggung jawab utama, kualifikasi yang dibutuhkan, dan informasi lain mengenai pelatihan ini.",
        height=200
    )

    link_video = st.text_input("Link embed dari youtube*", placeholder="Contoh: https://www.youtube.com/embed/xxxxxx")
    st.caption("Pastikan link yang Anda masukkan adalah link embed dari YouTube.")

    st.divider()

    submitted = st.form_submit_button("Unggah Pelatihan", type="primary", width="stretch")

if submitted:
    if not title or not description or not link_video or not uploaded_file:
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
            "thumbnail_course", 
            supabase_image_path, 
            content_type
        )

        if image_upload_success:
            st.toast("📤 Berhasil mengunggah file ke Storage!")
            data = {
                "user_id": user.user.id,
                "title": title,
                "description": description,
                "link_embeded": link_video,
                "thumbnail": supabase_image_path,
                "visibility": True
            }
            
            insert_success, insert_error = insert_courses(conn, data)
            if insert_success:
                st.success("🎉 Pelatihan berhasil diunggah!")
                st.switch_page("pages/pelatihan/list-pelatihan.py")
                st.rerun()
            else:
                st.error(f"Gagal menyimpan pelatihan: {insert_error}")

        else:
            st.error(f"Gagal mengunggah file: {image_upload_error}")
        