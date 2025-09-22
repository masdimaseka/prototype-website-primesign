import streamlit as st
from lib.supabase.connection import get_conn, get_session_and_user

st.set_page_config(
    page_title="Deteksi BISINDO",
    page_icon="🙌",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

conn = get_conn()
session, user = get_session_and_user(conn)

# top = st.container()
# with top:
#     st.markdown("### 🙌 Deteksi BISINDO")
    

# st.divider()

pages = {
    "Menu": [
        st.Page("pages/home.py", title="Home", icon="🏡"),
        st.Page("pages/list-kata.py", title="Kamus BISINDO", icon="📚"),
    ],

    "Job Board" : [
        st.Page("pages/job-board/list-job.py", title="Daftar Pekerjaan", icon="💼"),
    ],

    "Pelatihan" : [
        st.Page("pages/pelatihan/list-pelatihan.py", title="Daftar Pelatian", icon="🎓")
    ]
}

if user and user.user and user.user.user_metadata.get("role") == "recruiter":
    pages["Job Board"].append(
        st.Page("pages/job-board/upload-job.py", title="Unggah Pekerjaan", icon="⬆️")
    )
    pages["Job Board"].append(
        st.Page("pages/job-board/my-job.py", title="Unggahan Saya", icon="🔎")
    )

if user and user.user:
    pages["Pelatihan"].append(
        st.Page("pages/pelatihan/upload-pelatihan.py", title="Unggah Pelatihan", icon="⬆️")
    )
    pages["Pelatihan"].append(
        st.Page("pages/pelatihan/my-pelatihan.py", title="Pelatihan Saya", icon="🔎")
    )
    pages["Terjemahkan BISINDO"] = [
        st.Page("pages/detect-image.py", title="Deteksi dari Gambar", icon="📷"),
        st.Page("pages/detect-video.py", title="Deteksi dari Video", icon="📹"),
        st.Page("pages/detect-realTime.py", title="Deteksi Real Time", icon="📽️"),
    ]
    pages["Akun"] = [
        st.Page("pages/auth/profile.py", title="Profil", icon="👤"),
        st.Page("pages/auth/riwayat-deteksi.py", title="Riwayat", icon="🕘"),
    ]
else:
    pages["Deteksi BISINDO"] = [
        st.Page("pages/auth/sign-in.py", title="Sign In", icon="🔑"),
        st.Page("pages/auth/sign-up.py", title="Sign Up", icon="📝"),
    ]

pg = st.navigation(pages)
pg.run()
