# 🏡 PrimeSign - Menjembatani Komunikasi, Memberdayakan Sesama Melalui Teknologi AI

## 📌 Deskripsi

Proyek ini adalah aplikasi berbasis website yang dibuat untuk mendukung komunikasi serta kemandirian penyandang disabilitas, khususnya tunarungu dan tunawicara.

---

## ⚙️ Fitur Utama

- 🔑 **Autentikasi Multi-role** (User & Recruiter via Supabase)
- 📂 **Manajemen Data** (Upload dokumen/video/gambar ke Supabase Storage)
- 📊 **Deteksi & Translasi** (menggunakan model YOLO11)
- 📝 **Job Board** (unggah & kelola lowongan pekerjaan)
- 🎓 **Pelatihan** (kursus online dengan video)

---

## 🛠️ Instalasi Lokal

1. **Clone repo**

   ```bash
   git clone https://github.com/masdimaseka/prototype-website-primesign.git
   cd prototype-website-primesign
   ```

2. **Buat virtual environment** (opsional tapi direkomendasikan)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Mac/Linux
   .venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi**
   ```bash
   streamlit run app.py
   ```

---

## 🔑 Konfigurasi Environment

Buat file `.streamlit/secrets.toml` atau tambahkan ke Hugging Face Secrets:

```toml
[connections.supabase]
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "xxxxx"
bucket_name = "hasil_deteksi"
bucket_name_jobs = "jobs"
bucket_name_courses = "thumbnail_course"
```



Made by PrimeSign Team
