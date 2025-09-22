import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

def print_history_video(history_data_video):
    col1, col2, col3 = st.columns([4, 6, 2])
    with col1:
        st.markdown("**File & Waktu**")
    with col2:
        st.markdown("**Detail Deteksi**")
    with col3:
        st.markdown("**Aksi**")
    
    st.divider()

    for record in history_data_video:
        created_at_str = record.get("created_at")
        source_filename = record.get("source_filename", "N/A")
        config = record.get("config_used", "-")
        model = record.get("model_used", "-")
        video_path = record.get("caption_video_path")
        storage_path = record.get("storage_path")

        try:
            dt_object_utc = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            dt_object_wita = dt_object_utc.astimezone(ZoneInfo("Asia/Makassar"))

            formatted_time = dt_object_wita.strftime("%d %b %Y %H:%M:%S")
        except (ValueError, TypeError):
            formatted_time = "Waktu tidak valid"
        
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        bucket_name = st.secrets["bucket_name"]
        download_video_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{video_path}" if video_path else None
        download_zip_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{storage_path}" if storage_path else None

        col1, col2, col3 = st.columns([4, 6, 2])

        with col1:
            st.markdown(f"**{source_filename}**")
            st.caption(f"{formatted_time}")

        with col2:
            st.markdown(f"**Model:** {model}")
            st.markdown(f"Preset: {config}")
        
        with col3:
            if download_zip_url and download_video_url:
                st.link_button("⬇️ Lihat Video", download_video_url, width="stretch",)
                st.link_button("⬇️ Unduh .zip", download_zip_url, width="stretch",)

        st.divider()
