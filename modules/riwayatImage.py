import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

def print_history_image(history_data_image):
    col1, col2, col3 = st.columns([4, 6, 2])
    with col1:
        st.markdown("**File & Waktu**")
    with col2:
        st.markdown("**Detail Deteksi**")
    with col3:
        st.markdown("**Aksi**")
    
    st.divider()

    for record in history_data_image:
        created_at_str = record.get("created_at")
        source_filename = record.get("source_filename", "N/A")
        config = record.get("config_used", "-")
        model = record.get("model_used", "-")
        image_path = record.get("image_path")

        try:
            dt_object_utc = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            dt_object_wita = dt_object_utc.astimezone(ZoneInfo("Asia/Makassar"))

            formatted_time = dt_object_wita.strftime("%d %b %Y %H:%M:%S")
        except (ValueError, TypeError):
            formatted_time = "Waktu tidak valid"
        
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        bucket_name = st.secrets["bucket_name"]
        download_image_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{image_path}" if image_path else None

        col1, col2, col3 = st.columns([4, 6, 2])

        with col1:
            st.markdown(f"**{source_filename}**")
            st.caption(f"{formatted_time}")

        with col2:
            st.markdown(f"""**Model:** {model}""")
            st.markdown(f"Preset: conf: {config}")
        
        with col3:
            if download_image_url:
                st.link_button("⬇️ Lihat Image", download_image_url, width="stretch",)

        st.divider()
