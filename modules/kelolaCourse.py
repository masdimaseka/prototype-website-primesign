import streamlit as st
import uuid

from datetime import datetime
from lib.supabase.courses import update_courses
from lib.supabase.storage import delete_from_supabase, upload_to_supabase

@st.dialog(title="Detail Pelatihan", width="large")
def show_detail_course(link_video, title, description, data_user):
    st.markdown(
        f'<iframe width="100%" height="500" src="{link_video}"  frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>',
        unsafe_allow_html=True
    )   
    st.header(title)
    
    st.markdown(f'Posted by **{data_user.get("name")}**')
    
    st.divider()
    st.header("Deskripsi Pelatihan")
    st.text(description)


@st.dialog(title="Kelola Pelatihan", width="medium")
def manage_course(conn, course, user):
    st.subheader("📝 Ubah Detail Pelatihan")

    if 'processing' not in st.session_state:
        st.session_state.processing = False

    with st.form("edit_course_form"):
        st.subheader("Ganti Thumbnail (Opsional)")
        uploaded_file = st.file_uploader(
            "Unggah thumbnail baru jika ingin mengganti yang lama.",
            type=["png", "jpg", "jpeg"]
        )

        title = st.text_input("Judul Pelatihan*", placeholder="Contoh: Belajar Pemrograman Python", value=course.get("title", ""))
        description = st.text_area(
            "Deskripsi Pelatihan*",
            placeholder="Jelaskan tanggung jawab utama, kualifikasi yang dibutuhkan, dan informasi lain mengenai pelatihan ini.",
            height=200,
            value=course.get("description", "")
        )

        link_video = st.text_input("Link embed dari youtube*", placeholder="Contoh: https://www.youtube.com/embed/xxxxxx", value=course.get("link_embeded", ""))
        st.caption("Pastikan link yang Anda masukkan adalah link embed dari YouTube.")
        
        st.divider()

        st.subheader("Visibilitas Pelatihan")
        is_visible = course.get("visibility")
        new_visibility = st.checkbox("Publik", value=is_visible)

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
                    "user_id": user.user.id,
                    "title": title,
                    "description": description,
                    "link_embeded": link_video,
                    "visibility": new_visibility
                }

                if uploaded_file:
                    if course.get("thumbnail"):
                        success_del, err_del = delete_from_supabase(conn, "thumbnail_course", course.get("thumbnail"))
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
                        conn, file_bytes, "thumbnail_course", supabase_image_path, content_type
                    )

                    if not success_upload:
                        st.error(f"❌ Gagal mengunggah file baru: {err_upload}")
                        return 
                    
                    data_to_update["thumbnail"] = supabase_image_path

                update_success, update_error = update_courses(conn, course.get("id"), data_to_update)

                if update_success:
                    st.success("🎉 Perubahan berhasil disimpan!")
                    del st.session_state.processing 
                    st.rerun()
                else:
                    st.error(f"Gagal menyimpan perubahan ke database: {update_error}")

            finally:
                st.session_state.processing = False

                

           
           