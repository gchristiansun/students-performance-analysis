# Proyek Akhir: Student Success di Jaya Jaya Institut

## Business Understanding
Jaya Jaya Institut ingin menekan jumlah siswa yang tidak menyelesaikan studi. Data historis dapat membantu institusi memahami kaitan antara status akhir siswa, kemajuan akademik, dan beberapa indikator administrasi, lalu menentukan kelompok yang perlu ditinjau lebih awal.

### Permasalahan Bisnis
- Seberapa besar proporsi siswa yang berstatus Dropout, Graduate, dan Enrolled?
- Bagaimana nilai serta jumlah unit kurikulum yang lulus berbeda menurut status akhir?
- Dapatkah data akademik semester pertama dan kedua membantu mengidentifikasi siswa dengan risiko dropout lebih tinggi?

### Cakupan Proyek
- Menganalisis data historis untuk membandingkan status akhir, capaian akademik, dan indikator biaya kuliah.
- Menyajikan dashboard interaktif dengan filter dan visualisasi, bukan tabel saja.
- Melatih prototipe klasifikasi Random Forest untuk memperkirakan status Dropout menggunakan 10 fitur akademik dan administratif.
- Mendokumentasikan evaluasi, batas penggunaan model, cara menjalankan aplikasi, dan rekomendasi tindak lanjut.

### Persiapan
Sumber data: [Students' Performance Dataset](https://raw.githubusercontent.com/dicodingacademy/dicoding_dataset/main/students_performance/data.csv), dipublikasikan oleh Dicoding Academy. Data berisi 4.424 baris, 36 fitur, dan label `Status` (Dropout, Graduate, Enrolled). Data diambil saat aplikasi berjalan; koneksi internet diperlukan.

Setup environment (Python 3.11):
```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Business Dashboard
Dashboard berada pada halaman **Dashboard** di aplikasi Streamlit. Visualisasi menunjukkan komposisi status akhir, nilai rata-rata semester 1 dan 2 menurut status, serta unit kurikulum yang berhasil diselesaikan. KPI memperlihatkan jumlah siswa terfilter, tingkat dropout, tingkat kelulusan, dan proporsi biaya kuliah yang tercatat aktif. Filter usia, kode gender, dan status dapat digunakan untuk membandingkan profil kohort; data terfilter dapat diunduh dalam CSV.

Dataset ini adalah potret administratif historis tanpa ID siswa dan tanggal per semester, sehingga dashboard belum dapat menunjukkan tren waktu atau memantau siswa tertentu secara longitudinal.

## Menjalankan Sistem Machine Learning
Pilih halaman **Prediksi risiko** pada sidebar. Isi usia, status biaya/beasiswa/tunggakan, unit yang diambil dan lulus, serta nilai rata-rata untuk dua semester; tekan **Hitung estimasi**. Model final dilatih pada seluruh data dan disimpan oleh sel ekspor notebook sebagai `model/model.joblib`. Aplikasi memuat artefak tersebut saat dijalankan, bukan melatih model ulang. Jalankan notebook hingga sel ekspor untuk membuat atau memperbarui file model sebelum menjalankan aplikasi. Hasil prediksi adalah sinyal untuk ditinjau staf, bukan keputusan otomatis.

Sertakan `model/model.joblib` di repository saat deployment. Di Streamlit Community Cloud, pilih Python 3.11 pada **Advanced settings**; versi scikit-learn dipatok ke 1.6.1 agar sesuai dengan artefak model.

**URL aplikasi Streamlit Community Cloud:** 


## Evaluasi dan Kesimpulan
Target didefinisikan sebagai klasifikasi biner: `Dropout` dibandingkan `Graduate` dan `Enrolled`. Pada holdout stratified 20% dengan `random_state=42`, Random Forest mencapai akurasi **87,2%**, precision dropout **80,4%**, recall dropout **79,6%**, dan F1 dropout **80,0%** (2.209 Graduate, 1.421 Dropout, 794 Enrolled pada keseluruhan data). Dari 284 kasus dropout pada data uji, model mendeteksi 226 dan melewatkan 58; false positive juga perlu ditinjau.

Proporsi dropout keseluruhan adalah **32,1%**. Keterkaitan deskriptif dengan dropout terlihat lebih tinggi pada siswa dengan tunggakan (62,0% vs. 28,3% tanpa tunggakan) dan biaya kuliah yang belum tercatat lunas (86,6% vs. 24,7% yang tercatat lunas). Fitur teratas menurut importance model adalah jumlah unit lulus dan nilai semester kedua, disusul capaian semester pertama. Keterkaitan ini bukan bukti sebab-akibat.

**Kesimpulan:** institusi menghadapi proporsi dropout yang substansial. Capaian unit/nilai akademik dan status administrasi dapat menjadi sinyal untuk memprioritaskan peninjauan serta dukungan siswa. Prototipe menunjukkan baseline yang menjanjikan, tetapi menggunakan fitur hingga semester kedua; karena itu hasilnya belum merupakan sistem peringatan dini sebelum semester berjalan selesai. Validasi pada kohort baru, pemeriksaan fairness, dan evaluasi dampak intervensi diperlukan sebelum pemakaian operasional.

### Rekomendasi Action Items
- Jadwalkan konsultasi akademik bagi siswa dengan jumlah unit lulus atau nilai yang menurun/rendah, dan catat tindak lanjutnya.
- Tawarkan rujukan ke layanan keuangan bagi siswa yang memiliki tunggakan atau status pembayaran belum aktif; hindari menganggap status administrasi sebagai bukti penyebab dropout.
- Uji model secara prospektif pada kohort berikutnya dan ukur recall, precision, kalibrasi, serta performa per kelompok sebelum menentukan ambang intervensi.
- Audit potensi bias berdasarkan gender, usia, dan kelompok relevan lainnya; batasi akses data siswa dan jangan gunakan prediksi sebagai dasar sanksi atau keputusan akademik otomatis.
- Bangun pencatatan ID pseudonim dan snapshot semester berkala agar institusi dapat memantau perkembangan, tren, dan dampak program dukungan.
