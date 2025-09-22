import streamlit as st

from lib.supabase.connection import get_conn, get_session_and_user
from lib.supabase.courses import fetch_all_courses, delete_courses
from lib.supabase.storage import delete_from_supabase
from modules.kelolaCourse import manage_course

conn = get_conn()
session, user = get_session_and_user(conn)

st.title("Unggahan Pelatihan")
st.text("Kelola pelatihan anda.")
st.divider()

@st.dialog(title="Konfirmasi Hapus Pelatihan", width="small")
def confirm_delete_course(course, thumbnail, bucket_name):
    st.warning("⚠️ Anda yakin ingin menghapus pelatihan ini?")
    if st.button("Ya, Hapus Pelatihan Ini", use_container_width=True):
        success_del_img, error_del_img = delete_from_supabase(conn, bucket_name, thumbnail)
        if success_del_img:
            st.success("✅ File berhasil dihapus dari Supabase Storage.")

            success_del_course, error_del_course = delete_courses(conn, course.get("id"))
            if success_del_course:
                st.success("✅ pelatihan berhasil dihapus.")
            else:
                st.error(f"❌ Gagal menghapus pelatihan: {error_del_course}")
        else:
            st.error(f"❌ Gagal menghapus file: {error_del_img}")

        st.rerun()


all_courses = fetch_all_courses(conn)
            
SUPABASE_URL = st.secrets["SUPABASE_URL"]
bucket_name = st.secrets["bucket_name_courses"]

if not all_courses:
    st.info("Belum ada lowongan pelatihan yang tersedia saat ini. Silakan kembali lagi nanti.")
else:
    search_term = st.text_input("🔍 Cari Pelatihan", placeholder="Ketik pelatihan yang ingin Anda cari...")
    st.write("")
    filtered_courses = []
    if search_term:
        filtered_courses = [
            course for course in all_courses 
            if search_term.lower() in course.get("title", "").lower()
        ]
    else:
        filtered_courses = all_courses

    if not filtered_courses:
        st.warning(f"Tidak ada pelatihan")
    else:
        for index, course in enumerate(filtered_courses):
            with st.container(border=True):
                thumbnail = course.get("thumbnail")
                thumbnail_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{thumbnail}" if thumbnail else None
            
                col1, col2 = st.columns(2, gap="large")

                with col1:
                    if thumbnail_url:
                        st.image(thumbnail_url)
                        
                with col2:
                    title = course.get("title", "-")
                    st.subheader(title) 

                    if user and user.user:
                        st.markdown(f'Posted by **{user.user.user_metadata.get("display_name", "-")}**')

                    with st.container(horizontal=True):
                        st.text("Visibilitas:")
                        if course.get("visibility"):
                            st.badge("Publik", color="green")
                        else:
                            st.badge("Pribadi", color="red")

                st.divider()

                description = course.get("description")
                link_video = course.get("link_embeded", "-")

                if st.button("Kelola Pelatihan", type="primary", use_container_width=True, key=f"btn_{course.get('id')}"):
                    manage_course(conn, course, user)

                if st.button("Hapus Pelatihan", type="secondary", use_container_width=True, key=f"btn_delete_{course.get('id')}"):
                    confirm_delete_course(course, thumbnail, bucket_name)
                    

                st.write("")



