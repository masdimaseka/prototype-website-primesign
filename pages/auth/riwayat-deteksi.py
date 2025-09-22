import streamlit as st


from lib.supabase.connection import get_conn
from lib.supabase.image_history import fetch_detection_image_history
from lib.supabase.video_history import fetch_detection_video_history
from modules.riwayatVideo import print_history_video
from modules.riwayatImage import print_history_image

st.set_page_config(page_title="Riwayat Deteksi", page_icon="📜", layout="wide")

st.header("📜 Riwayat Deteksi")
st.text("Menampilkan semua riwayat deteksi yang tersimpan di database.")

if st.button("🔄 Segarkan Data"):
    st.cache_data.clear()
    st.toast("Data riwayat telah disegarkan!")

try:
    conn = get_conn()
    history_data_video = fetch_detection_video_history(conn)
    history_data_image = fetch_detection_image_history(conn)

    tab1_r_video, tab2_r_image = st.tabs(["Riwayat Deteksi Video", "Riwayat Deteksi Gambar"])

    with tab1_r_video:
        print_history_video(history_data_video)
    with tab2_r_image:
        print_history_image(history_data_image)
        

    

except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat riwayat: {e}")