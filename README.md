# 📊 Usage Dashboard

Dashboard analitik interaktif yang dibangun menggunakan **Python (Streamlit)** untuk menampilkan **data penggunaan (usage)** dan **data amount (dpp & ppn)** perusahaan berdasarkan sumber data Excel.  
Proyek ini bertujuan untuk mempermudah analisis dan visualisasi data perusahaan tanpa perlu menggunakan tools BI eksternal seperti Power BI atau Tableau.

---

## 🚀 Fitur Utama

- 📈 **Visualisasi Interaktif** — menampilkan grafik tren, distribusi, dan Top 10 perusahaan berdasarkan data usage.
- 🧮 **Pemrosesan Data Excel Otomatis** — membaca dan mengolah data dari file `.xlsx` secara dinamis.
- 🏢 **Analisis Berdasarkan Perusahaan** — menampilkan total usage, rata-rata, dan perbandingan antar perusahaan.
- ⚙️ **Modular & Mudah Dikembangkan** — struktur kode berbasis native.
- 💾 **Tanpa Database Eksternal** — metode pembacaan file Excel untuk menjalankan analisis.

---

## 🧰 Teknologi yang Digunakan

| Komponen | Deskripsi |
|-----------|------------|
| **Python 3.10+** | Bahasa pemrograman utama |
| **Streamlit** | Framework untuk dashboard interaktif |
| **Pandas** | Analisis dan manipulasi data |
| **Plotly / Matplotlib** | Visualisasi data |
| **OpenPyXL** | Pembacaan file Excel |

---

## 📂 Struktur Folder

```bash
usage-dashboard/
│
├── dashboard.py          # File utama Streamlit
├── usage-company.xlsx    # Dataset contoh (dummy)
├── requirements.txt      # Daftar dependensi Python
└── README.md             # Dokumentasi proyek
