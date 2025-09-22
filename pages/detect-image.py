import streamlit as st
import cv2
import uuid

from datetime import datetime
from modules.loadModel import load_model_files
from modules.processImage import process_image
from modules.infoModel import model_detail_dialog
from lib.supabase.connection import get_conn, get_session_and_user
from lib.supabase.storage import upload_to_supabase
from lib.supabase.image_history import insert_detection_image_history

conn = get_conn()
session, user = get_session_and_user(conn)

if not user or not user.user:
    st.warning("Anda harus login untuk mengakses halaman ini.")
    st.stop()

st.set_page_config(page_title="Detect Image", page_icon="🖼️")
st.title("Deteksi dari Gambar")
st.text("Deteksi objek pada gambar menggunakan model YOLO")
st.divider()

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False
if "proc_params" not in st.session_state:
    st.session_state.proc_params = None
if "image_result" not in st.session_state:
    st.session_state.image_result = None
if "uploader_key_img" not in st.session_state:
    st.session_state.uploader_key_img = 0

def clear_state():
    st.session_state.is_processing = False
    st.session_state.img_bytes = None
    st.session_state.image_result = None
    st.session_state.uploader_key_img += 1
    st.rerun()

models = load_model_files()
col_left, col_right = st.columns([3, 6], gap="large")

with col_left:
    st.subheader("Pilih Model")
    if not models:
        st.error("Tidak ada model (.pt) yang ditemukan di folder 'weights'!")
        st.stop()
    else:
        with st.container(border=True):
            selected_model = st.selectbox(
                "Pilih model yang akan digunakan",
                models,
                index=0,
                key="sb_model_img"
            )
            if st.button("Lihat Spesifikasi Model", type="secondary", width="stretch", ):
                model_detail_dialog(selected_model)

    st.divider()
    st.subheader("Konfigurasi")
    with st.container(border=True):
        conf = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.70,  
            step=0.01
        )
        st.info("Hanya objek dengan tingkat kepercayaan di atas nilai ini yang akan ditampilkan.")

with col_right:
    st.subheader("Upload & Deteksi Gambar")
    uploaded_file = st.file_uploader(
        "Upload sebuah gambar",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False,
        key=f"uploader_{st.session_state.uploader_key_img}",
        disabled=st.session_state.is_processing,
    )

    if uploaded_file and not st.session_state.is_processing and st.session_state.image_result is None:
        st.image(uploaded_file, width="stretch")
        

    start_disabled = st.session_state.is_processing or not uploaded_file or not selected_model
    if st.button("🚀 Mulai Deteksi", type="primary", width="stretch", disabled=start_disabled):
            st.session_state.is_processing = True
            st.session_state.proc_params = {
                "image_bytes": uploaded_file.getvalue(),
                "model_path" : f"weights/{selected_model}",
                "cfg": conf,
                "source_filename": getattr(uploaded_file, "name", "uploaded_image.png"),
            } 
            st.rerun()
            
    if st.session_state.is_processing and st.session_state.proc_params:
        with st.spinner("⏳ Memproses gambar..."):
            try:
                params = st.session_state.proc_params
                result_img_bgr = process_image(params["image_bytes"], params["model_path"], params["cfg"])

                result_img_rgb = cv2.cvtColor(result_img_bgr, cv2.COLOR_BGR2RGB)

                _, buf = cv2.imencode(".png", result_img_bgr)
                st.session_state.image_result = buf.tobytes()

                st.toast("✅ Deteksi selesai!")

                with st.spinner("Mengunggah hasil dan menyimpan riwayat..."):
                    original_filename = params["source_filename"].rsplit('.', 1)[0]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_id = str(uuid.uuid4()).split('-')[0]
                    
                    image_file_name = f"{original_filename}_{timestamp}_{unique_id}_caption.png"
                    
                    supabase_image_path = f"{user.user.id}/{image_file_name}"
                    
                    image_upload_success, image_upload_error = upload_to_supabase(conn, st.session_state.image_result, "hasil_deteksi", supabase_image_path, "image/png")

                    if image_upload_success:
                        st.toast("📤 Berhasil mengunggah file ke Storage!")
                        history_record = {
                            "user_id": user.user.id,
                            "source_filename": params["source_filename"],
                            "model_used": params["model_path"].split('/')[-1],
                            "config_used": params["cfg"],
                            "image_path": supabase_image_path,
                        }
                        insert_success, insert_error = insert_detection_image_history(conn, history_record)
                        if insert_success:
                            st.success("✔️ Riwayat deteksi berhasil disimpan!")
                        else:
                            st.error(f"Gagal menyimpan riwayat: {insert_error}")
                    else:
                        st.error(f"Gagal mengunggah file. Video: {image_upload_error}")

                       
                    st.divider()

                    st.subheader("Hasil Deteksi")
                    st.image(result_img_rgb, width="stretch")

                    st.download_button(
                        label="⬇️ Download Hasil Gambar",
                        data=st.session_state.image_result,
                        file_name=f"hasil_{original_filename}.png",
                        mime="image/png",
                        width="stretch",
                        type="primary"
                    )
                    
                    if st.button("🆕 Lakukan deteksi baru", width="stretch"):
                        clear_state()

            except Exception as e:
                st.error(f"❌ Terjadi kesalahan saat pemrosesan: {e}")
            finally:
                if st.session_state.is_processing:
                    st.session_state.is_processing = False