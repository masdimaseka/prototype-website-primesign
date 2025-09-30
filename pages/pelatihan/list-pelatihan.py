import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

from lib.supabase.connection import get_conn, get_session_and_user
from lib.supabase.courses import fetch_all_courses
from lib.supabase.profile_recruiter import fetch_profile_recruiter_by_id
from lib.supabase.profile import fetch_profile_by_id
from modules.kelolaCourse import show_detail_course

conn = get_conn()
session, user = get_session_and_user(conn)

st.title("Daftar Pelatihan")
st.text("Temukan peluang karir terbaru yang tersedia untuk Anda.")
st.divider()

@st.dialog(title="Tidak dapat diakses", width="small")
def no_access_dialog():
    st.warning("Anda harus masuk untuk mengakses halaman ini.")

all_courses = fetch_all_courses(conn)
            
SUPABASE_URL = st.secrets["SUPABASE_URL"]
bucket_name = st.secrets["bucket_name_courses"]

if not all_courses:
    st.info("Belum ada lowongan pekerjaan yang tersedia saat ini. Silakan kembali lagi nanti.")
else:
    visible_courses = [job for job in all_courses if job.get("visibility") is True]
    search_term = st.text_input("🔍 Cari Pelatihan", placeholder="Ketik pelatihan yang ingin Anda cari...")
    st.write("")
    filtered_courses = []
    if search_term:
        filtered_courses = [
            course for course in visible_courses 
            if search_term.lower() in course.get("title", "").lower()
        ]
    else:
        filtered_courses = visible_courses

    if not filtered_courses:
        st.warning(f"Tidak ada pelatihan")
    else:

        col1, col2 = st.columns(2, gap="large")

        for index, course in enumerate(filtered_courses):
            
            if index % 2 == 0:
                with col1:
                    with st.container(border=True):
                        thumbnail = course.get("thumbnail")
                        thumbnail_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{thumbnail}" if thumbnail else None
                        
                        if thumbnail_url:
                            st.image(thumbnail_url)
                        
                        title = course.get("title", "-")
                        st.subheader(title) 

                        created_at_str = course.get("created_at")
                        try:
                            dt_object_utc = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                            dt_object_wita = dt_object_utc.astimezone(ZoneInfo("Asia/Makassar"))

                            formatted_time = dt_object_wita.strftime("%d %b %Y %H:%M:%S")
                        except (ValueError, TypeError):
                            formatted_time = "Waktu tidak valid"
                        st.caption(f"{formatted_time}")


                        data_user, error = fetch_profile_by_id(conn, course.get("user_id"))

                        if data_user is None:
                            data_user, error = fetch_profile_recruiter_by_id(conn, course.get("user_id"))


                        st.markdown(f'Posted by **{data_user.get("name")}**')

                        st.divider()

                        description = course.get("description")
                        link_video = course.get("link_embeded", "-")

                        if st.button("Lihat Pelatihan", type="secondary", use_container_width=True, key=f"btn_{course.get('id')}"):
                            if not user:
                                    no_access_dialog()
                            else:
                                show_detail_course(link_video, title, description, data_user)
                
                    st.write("") 

            else:
                with col2:
                    with st.container(border=True):
                        thumbnail = course.get("thumbnail")
                        thumbnail_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{thumbnail}" if thumbnail else None
                        
                        if thumbnail_url:
                            st.image(thumbnail_url)
                        
                        title = course.get("title", "-")
                        st.subheader(title) 

                        created_at_str = course.get("created_at")
                        try:
                            dt_object_utc = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                            dt_object_wita = dt_object_utc.astimezone(ZoneInfo("Asia/Makassar"))

                            formatted_time = dt_object_wita.strftime("%d %b %Y %H:%M:%S")
                        except (ValueError, TypeError):
                            formatted_time = "Waktu tidak valid"
                        st.caption(f"{formatted_time}")

                        
                        data_user, error = fetch_profile_by_id(conn, course.get("user_id"))

                        if data_user is None:
                            data_user, error = fetch_profile_recruiter_by_id(conn, course.get("user_id"))


                        st.markdown(f'Posted by **{data_user.get("name")}**')

                        st.divider()

                        description = course.get("description")
                        link_video = course.get("link_embeded", "-")

                        if st.button("Lihat Pelatihan", type="secondary", use_container_width=True, key=f"btn_{course.get('id')}"):
                            if not user:
                                    no_access_dialog()
                            else:
                                show_detail_course(link_video, title, description, data_user)
                
                    st.write("")
                    



