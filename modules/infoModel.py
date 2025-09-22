import streamlit as st

MODEL_DETAILS = {
    "model-bisindo-yolo11-v8a.pt": {
        "model_name": "YOLOv11s",
        "accuracy": "89%",
        "num_classes": 36,
        "class_list": [
            "apa", "bagaimana", "baik", "belajar", "berapa", "berdiri", 
            "bingung", "dimana", "duduk", "halo", "kabar", "kalian", 
            "kami", "kamu", "kapan", "kemana", "makan", "malam", 
            "mandi", "marah", "melihat", "menulis", "mereka", "minum", 
            "pagi", "ramah", "sabar", "saya", "sedih", "selamat", 
            "senang", "siang", "siapa", "sore", "terima kasih", "tidur"
        ]
    },
    "bisindo-yolo11-v12a.pt": {
        "model_name": "YOLOv11s",
        "accuracy": "89%",
        "num_classes": 36,
        "class_list": [
            "apa", "bagaimana", "baik", "belajar", "berapa", "berdiri", 
            "bingung", "dimana", "duduk", "halo", "kabar", "kalian", 
            "kami", "kamu", "kapan", "kemana", "makan", "malam", 
            "mandi", "marah", "melihat", "menulis", "mereka", "minum", 
            "pagi", "ramah", "sabar", "saya", "sedih", "selamat", 
            "senang", "siang", "siapa", "sore", "terima kasih", "tidur"
        ]
    },
}

@st.dialog(title="Detail Model", width="medium")
def model_detail_dialog(selected_model: str):
    st.badge(selected_model, color="green")

    details = MODEL_DETAILS.get(selected_model)

    if details:
        st.markdown(f"""
        - **Model:** `{details["model_name"]}`
        - **Akurasi Model:** `{details["accuracy"]}`
        - **Jumlah Kelas:** `{details["num_classes"]} Kelas`
        """)

        st.markdown("**Daftar Kelas yang Dapat Dikenali:**")
        class_string = ", ".join(details["class_list"])
        st.info(class_string)
    else:
        st.warning(f"Detail untuk model '{selected_model}' tidak ditemukan.")