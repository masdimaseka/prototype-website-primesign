import streamlit as st
import pandas as pd
import io
import zipfile
import uuid
from collections import Counter
from datetime import datetime

from modules.loadModel import load_model_files
from modules.config import get_preset, override_config 
from modules.processVideo import process_video
from modules.infoVideo import read_video_info
from modules.infoModel import model_detail_dialog
from lib.supabase.connection import get_conn, get_session_and_user
from lib.supabase.storage import upload_to_supabase
from lib.supabase.video_history import insert_detection_video_history

@st.cache_resource
def init_supabase_connection():
    return get_conn()

conn = init_supabase_connection()
session, user = get_session_and_user(conn)

if not user or not user.user:
    st.warning("Anda harus login untuk mengakses halaman ini.")
    st.stop()

st.set_page_config(page_title="Detect Video", page_icon="🎥")
st.title("Deteksi dari Video")
st.text("Deteksi objek pada video menggunakan YOLO")
st.divider()

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False
if "proc_params" not in st.session_state:
    st.session_state.proc_params = None
if "last_boxes_bytes" not in st.session_state:
    st.session_state.last_boxes_bytes = None
if "last_caption_bytes" not in st.session_state:
    st.session_state.last_caption_bytes = None
if "last_srt_text" not in st.session_state:
    st.session_state.last_srt_text = None
if "tmp_video_path" not in st.session_state:
    st.session_state.tmp_video_path = None
if "video_info" not in st.session_state:
    st.session_state.video_info = None
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

def clear_state(): 
    keys_to_reset = [
        "proc_params", 
        "last_boxes_bytes", 
        "last_caption_bytes", 
        "last_srt_text", 
        "video_info",
        "tmp_video_path"
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            st.session_state[key] = None
            
    st.session_state.is_processing = False
    st.session_state.uploader_key += 1
    st.rerun()

def get_detection_summary(srt_text: str):
    if not srt_text or not srt_text.strip():
        return None
    labels = [line.strip() for block in srt_text.strip().split('\n\n') if len(lines := block.split('\n')) >= 3 and (line := lines[2])]
    return Counter(labels) if labels else None

models = load_model_files()
col_left, col_right = st.columns([3, 6], gap="large")

with col_left:
    st.subheader("Pilih Model")
    if not models:
        st.error("Tidak ada model (.pt) yang ditemukan di folder 'weights'!")
        st.stop()
    else:
        with st.container(border=True):
            selected_model = st.selectbox("Pilih model yang akan digunakan", models, index=0)
            
            if st.button("Lihat Spesifikasi Model", type="secondary", width="stretch", disabled=st.session_state.is_processing): 
                model_detail_dialog(selected_model)

    st.divider()
    st.subheader("Konfigurasi")
    tab_basic, tab_adv = st.tabs(["⚙️ Basic", "🛠️ Advance"])

    with tab_basic:
        preset_name = st.selectbox(
            "Preset Konfigurasi",
            options=("Cepat", "Seimbang (rekomendasi)", "Akurat"),
            index=1,
            disabled=st.session_state.is_processing,
        )
        base_cfg = get_preset(preset_name)
        with st.expander("Ringkasan Preset", expanded=True):
            st.markdown(f"""
            - **Confidence**: `{base_cfg['conf']}`
            - **IoU**: `{base_cfg['iou']}`
            - **Target FPS (sampling)**: `{base_cfg['target_fps']}`
            - **Window Voting**: `{base_cfg['window_vote']}`
            - **Frame Konsisten**: `{base_cfg['cons_frame']}`
            - **Start Threshold**: `{base_cfg['start_threshold']}`
            - **Stop Threshold**: `{base_cfg['end_threshold']}`
            """)
        st.info("Nilai di tab **Advance** akan menimpa (override) preset ini.")

    with tab_adv:
        conf = st.slider("Confidence Threshold", 0.0, 1.0, base_cfg['conf'], 0.01, disabled=st.session_state.is_processing)
        iou = st.slider("IoU Threshold (NMS)", 0.1, 0.9, base_cfg['iou'], 0.01, disabled=st.session_state.is_processing)
        target_fps = st.slider("Target FPS (sampling)", 1, 60, base_cfg['target_fps'], 1, disabled=st.session_state.is_processing)
        window_vote = st.slider("Ukuran Window Voting (frame)", 3, 60, base_cfg['window_vote'], 1, disabled=st.session_state.is_processing)
        cons_frame = st.slider("Frame Konsisten Dibutuhkan", 1, 30, base_cfg['cons_frame'], 1, disabled=st.session_state.is_processing)
        start_threshold = st.slider("Start Threshold (hysteresis)", 0.1, 1.0, base_cfg['start_threshold'], 0.05, disabled=st.session_state.is_processing)
        end_threshold = st.slider("Stop Threshold (hysteresis)", 0.1, 1.0, base_cfg['end_threshold'], 0.05, disabled=st.session_state.is_processing)

    cfg = override_config(base_cfg, conf=conf, iou=iou, target_fps=target_fps, window_vote=window_vote, cons_frame=cons_frame, start_threshold=start_threshold, end_threshold=end_threshold)


with col_right:
    st.subheader("Upload & Deteksi Video")
    uploaded = st.file_uploader("Upload Video", type=["mp4"], accept_multiple_files=False, disabled=st.session_state.is_processing, key=f"uploader_{st.session_state.uploader_key}")

    if uploaded and not st.session_state.is_processing and st.session_state.last_caption_bytes is None:
        video_bytes = uploaded.getvalue()
        st.video(video_bytes)
        try:
            _, info = read_video_info(video_bytes)
            st.session_state.video_info = info
            st.markdown(f"""
            **Detil Video**
            - Resolusi: `{info['resolution']}`
            - FPS: `{info['fps']}`
            - Frame: `{info['frames']}`
            - Durasi: `{info['duration_s']:.2f} s`
            """)
        except Exception as e:
            st.warning(f"Tidak bisa membaca metadata video: {e}")

    start_disabled = st.session_state.is_processing or not uploaded or not selected_model
    if st.button("🚀 Mulai Deteksi", width="stretch", type="primary", disabled=start_disabled): 
        st.session_state.is_processing = True
        st.session_state.proc_params = {
            "file_bytes": uploaded.getvalue(),
            "model_path": f"weights/{selected_model}",
            "cfg": cfg,
            "preset_name": preset_name,
            "source_filename": getattr(uploaded, "name", "uploaded_video.mp4"),
            "video_info": st.session_state.video_info
        }
        st.rerun()

    if st.session_state.is_processing and st.session_state.proc_params:
        progress_bar = st.progress(0, text="Memulai pemrosesan...")
        info_box = st.empty()

        def on_progress(done, total, label):
            progress = min(done / total, 1.0) if total > 0 else 0
            progress_bar.progress(progress, text=f"Memproses frame: {done}/{total}")
            info_box.info(f"Label terdeteksi saat ini: {label or '---'}")

        try:
            params = st.session_state.proc_params
            boxes_path, caption_path, srt_text = process_video(
                file_bytes=params["file_bytes"], model_path=params["model_path"],
                cfg=params["cfg"], progress_cb=on_progress
            )
            
            with open(boxes_path, "rb") as f: st.session_state.last_boxes_bytes = f.read()
            with open(caption_path, "rb") as f: st.session_state.last_caption_bytes = f.read()
            st.session_state.last_srt_text = srt_text
            st.toast("✅ Video selesai diproses!")

            st.subheader("📊 Ringkasan Deteksi")
            label_counts = get_detection_summary(srt_text)
            if label_counts:
                df_summary = pd.DataFrame(label_counts.items(), columns=["Label Terdeteksi", "Jumlah Kemunculan"])
                st.dataframe(df_summary, width="stretch", hide_index=True)
            else:
                st.info("Tidak ada objek yang terdeteksi untuk ditampilkan dalam ringkasan.")
            st.divider()

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("hasil_boxes_only.mp4", st.session_state.last_boxes_bytes)
                zf.writestr("hasil_caption_only.mp4", st.session_state.last_caption_bytes)
                if srt_text and srt_text.strip():
                    zf.writestr("hasil_deteksi.srt", srt_text.encode("utf-8"))
            zip_bytes = zip_buffer.getvalue()

            with st.spinner("Mengunggah hasil dan menyimpan riwayat..."):
                original_filename = params["source_filename"].rsplit('.', 1)[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4()).split('-')[0]
                
                zip_file_name = f"{original_filename}_{timestamp}_{unique_id}.zip"
                video_file_name = f"{original_filename}_{timestamp}_{unique_id}_caption.mp4"
                
                supabase_zip_path = f"{user.user.id}/{zip_file_name}"
                supabase_video_path = f"{user.user.id}/{video_file_name}"
                
                video_upload_success, video_upload_error = upload_to_supabase(conn, st.session_state.last_caption_bytes, "hasil_deteksi", supabase_video_path, "video/mp4")
                zip_upload_success, zip_upload_error = upload_to_supabase(conn, zip_bytes, "hasil_deteksi", supabase_zip_path, "application/zip" )

                if video_upload_success and zip_upload_success:
                    st.toast("📤 Berhasil mengunggah file ke Storage!")
                    history_record = {
                        "user_id": user.user.id,
                        "source_filename": params["source_filename"],
                        "model_used": params["model_path"].split('/')[-1],
                        "config_used": params["cfg"],
                        "duration_s": params.get("video_info", {}).get('duration_s', 0.0),
                        "detection_summary": dict(label_counts) if label_counts else {},
                        "storage_path": supabase_zip_path,
                        "caption_video_path": supabase_video_path,
                    }
                    insert_success, insert_error = insert_detection_video_history(conn, history_record)
                    if insert_success:
                        st.success("✔️ Riwayat deteksi berhasil disimpan!")
                    else:
                        st.error(f"Gagal menyimpan riwayat: {insert_error}")
                else:
                    st.error(f"Gagal mengunggah file. Video: {video_upload_error}, Zip: {zip_upload_error}")
            
            st.subheader("Hasil Deteksi")
            st.video(st.session_state.last_caption_bytes)
            st.download_button(
                label="⬇️ Download Video Hasil", data=st.session_state.last_caption_bytes,
                file_name=f"hasil_{original_filename}.mp4", mime="video/mp4" ,
                width="stretch", type="primary"
            )
            st.divider()
            
            st.subheader("Download Semua Hasil (.zip)")
            st.download_button(
                label="⬇️ Download Video + Subtitle + SRT", data=zip_bytes,
                file_name=f"hasil_lengkap_{original_filename}.zip", mime="application/zip",
                width="stretch", type="secondary"
            )
            st.divider()

            if st.button("🆕 Lakukan deteksi baru", width="stretch"): 
                clear_state()

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan saat pemrosesan: {e}")
        finally:
            progress_bar.empty()
            info_box.empty()
            if st.session_state.is_processing:
                st.session_state.is_processing = False