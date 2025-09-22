import streamlit as st
import cv2

from modules.loadModel import load_model_files
from modules.infoModel import model_detail_dialog
from modules.processRealtime import process_frame

st.set_page_config(page_title="Detect Realtime", page_icon="📽️")
st.title("Deteksi Bahasa Isyarat Real Time")
st.text("Deteksi secara real time menggunakan model YOLO yang telah dilatih.")
st.divider()

if "stop_detection" not in st.session_state:
    st.session_state.stop_detection = True
if "detected_sequence" not in st.session_state:
    st.session_state.detected_sequence = []


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
                key="sb_model_realtime"
            )

            if st.button("Lihat Spesifikasi Model", type="secondary", width="stretch", disabled=not st.session_state.stop_detection): 
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
    st.subheader("Kontrol Deteksi")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Mulai Deteksi", type="primary", use_container_width=True, disabled=not st.session_state.stop_detection):
            st.session_state.stop_detection = False
            st.session_state.detected_sequence = []
            st.rerun()

    with col2:
        if st.button("⏹️ Hentikan Deteksi", type="secondary", use_container_width=True, disabled=st.session_state.stop_detection):
            st.session_state.stop_detection = True
            st.rerun()

    st.divider()
    
    st.subheader("Tampilan Kamera")
    frame_placeholder = st.image([])
    info_placeholder = st.empty() 

    if not st.session_state.stop_detection:
        try:
            model_path = f"weights/{selected_model}"

            if model_path:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    st.error("❌ Gagal membuka kamera. Pastikan kamera terhubung dan tidak digunakan aplikasi lain.")
                else:
                    while not st.session_state.stop_detection and cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            st.warning("Gagal menerima frame. Deteksi dihentikan.")
                            break
                        
                        annotated_frame, detected_classes = process_frame(model_path, frame, conf)
                        
                        if len(detected_classes) == 1:
                            current_sign = list(detected_classes)[0]
                            if not st.session_state.detected_sequence or st.session_state.detected_sequence[-1] != current_sign:
                                st.session_state.detected_sequence.append(current_sign)
                        
                        frame_placeholder.image(annotated_frame)
                        
                        if st.session_state.detected_sequence:
                            info_placeholder.success(f"Kalimat Terdeteksi: {' '.join(st.session_state.detected_sequence)}")
                        else:
                            info_placeholder.info("Arahkan isyarat ke kamera...")
                    
                    cap.release()
                    
        except Exception as e:
            st.error(f"Terjadi kesalahan saat pemrosesan: {e}")
            st.session_state.stop_detection = True
            
    else:
        st.info("Tekan 'Mulai Deteksi' untuk mengaktifkan kamera.")

        
        if st.session_state.detected_sequence:
            st.divider()
            
            st.subheader("Hasil deteksi")
            st.success(f"Kalimat akhir yang tercatat: {' '.join(st.session_state.detected_sequence)}")
            if st.button("Bershikan riwayat deteksi", type="secondary", width="stretch"):
                st.session_state.detected_sequence.clear()