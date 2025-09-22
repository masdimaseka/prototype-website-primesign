import streamlit as st
from lib.supabase.connection import get_conn
from lib.supabase.kata_bisindo import fetch_kata_bisindo

st.set_page_config(page_title="Kamus BISINDO", page_icon="🤟", layout="wide")


st.title("Kamus Bahasa Isyarat Indonesia (BISINDO)")
st.text("Jelajahi dan pelajari berbagai kosakata dalam BISINDO.")

st.divider()

@st.dialog(title="Video Gerakan", width="medium")
def show_video(word_title: str, video_url: str):
    st.subheader(word_title)
    st.video(video_url, autoplay=True, loop=True, muted=True)

conn = get_conn()
words_data = fetch_kata_bisindo(conn)

if not words_data:
    st.info("Saat ini belum ada kata yang tersedia di kamus.")
    st.stop()

search_term = st.text_input("🔍 Cari Kata", placeholder="Ketik kata yang ingin Anda cari...")

if search_term:
    filtered_data = [
        word for word in words_data
        if search_term.lower() in word.get("word", "").lower()
    ]
else:
    filtered_data = words_data

if not filtered_data:
    st.warning(f"Tidak ada hasil yang cocok untuk '{search_term}'.")
else:
    st.markdown(f"**Menampilkan {len(filtered_data)} kata:**")

    for index, word in enumerate(filtered_data):
        with st.container(border=True):
            word_title = word.get("word", "Tanpa Nama").replace("_", " ").title()
            video_url = word.get("video_path")
            
            st.subheader(word_title)

            if video_url:
                if st.button("Lihat Gerakan", type="secondary", key=f"btn_{word.get('id', index)}"):
                    show_video(word_title, video_url)
            else:
                st.warning("URL Video tidak tersedia.")