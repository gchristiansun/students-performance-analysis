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
- Melatih prototipe klasifikasi biner Random Forest dengan target `1 = Dropout` dan `0 = Graduate`, menggunakan 10 fitur akademik dan administratif. Siswa berstatus Enrolled dipisahkan dan tidak digunakan saat training atau evaluasi.
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
Dashboard berada pada halaman **Dashboard** di aplikasi Streamlit. Visualisasi menunjukkan komposisi status akhir, nilai rata-rata dan unit kurikulum per semester, tingkat Dropout menurut tunggakan/status pembayaran/beasiswa, serta tingkat Dropout menurut rentang unit lulus semester 2. Hover pada grafik faktor menampilkan jumlah siswa tiap kelompok. Analisis tingkat Dropout hanya memakai siswa berstatus Dropout atau Graduate; Enrolled tidak dihitung sebagai hasil akhir. Distribusi usia, KPI, filter usia/gender/status, dan unduhan CSV juga tersedia. Hubungan faktor dengan status bersifat deskriptif, bukan bukti sebab-akibat.

Dataset ini adalah potret administratif historis tanpa ID siswa dan tanggal per semester, sehingga dashboard belum dapat menunjukkan tren waktu atau memantau siswa tertentu secara longitudinal.

## Menjalankan Sistem Machine Learning
Pilih halaman **Prediksi risiko** pada sidebar. Isi usia, status biaya/beasiswa/tunggakan, unit yang diambil dan lulus, serta nilai rata-rata untuk dua semester; tekan **Hitung estimasi**. Target model adalah `1 = Dropout` dan `0 = Graduate`. Model final hanya dilatih pada baris berstatus Dropout atau Graduate dan disimpan oleh sel ekspor notebook sebagai `model/model.joblib`. Baris Enrolled tetap terpisah dari training/evaluasi; notebook menggunakan model final untuk menghasilkan estimasi status dan probabilitas dropout bagi baris Enrolled yang memiliki fitur lengkap. Aplikasi memuat artefak tersebut saat dijalankan, bukan melatih model ulang. Jalankan notebook hingga sel ekspor untuk membuat atau memperbarui file model sebelum menjalankan aplikasi. Hasil prediksi adalah sinyal untuk ditinjau staf, bukan keputusan otomatis.

Sertakan `model/model.joblib` di repository saat deployment. Di Streamlit Community Cloud, pilih Python 3.11 pada **Advanced settings**; versi scikit-learn dipatok ke 1.6.1 agar sesuai dengan artefak model.

**URL aplikasi Streamlit Community Cloud:** 
https://analyse-students-performance.streamlit.app

## Evaluasi dan Kesimpulan
Target didefinisikan sebagai klasifikasi biner: `Dropout = 1` dan `Graduate = 0`; 794 siswa Enrolled dikeluarkan dari pemodelan. Dari 4.424 baris sumber, 3.630 baris Dropout/Graduate digunakan untuk pemodelan (2.209 Graduate dan 1.421 Dropout). Pada holdout stratified 20% dengan `random_state=42` (442 Graduate dan 284 Dropout), Random Forest mencapai akurasi **90,8%**, precision dropout **88,1%**, recall dropout **88,4%**, dan F1 dropout **88,2%**. Model mendeteksi 251 dari 284 kasus dropout dan melewatkan 33; sebanyak 34 Graduate salah ditandai sebagai Dropout. Siswa Enrolled tidak masuk angka evaluasi tersebut.

Proporsi Dropout dari seluruh kohort adalah **32,1%**. Pada perbandingan Dropout/Graduate (Enrolled dikeluarkan dari penyebut), tingkat Dropout adalah 75,5% pada kelompok dengan tunggakan vs. 34,5% tanpa tunggakan, 94,0% pada biaya yang belum tercatat lunas vs. 30,7% yang tercatat lunas, dan 48,4% tanpa beasiswa vs. 13,8% dengan beasiswa. Berdasarkan unit lulus semester 2, tingkat Dropout adalah 92,1% untuk 0–2 unit, 36,4% untuk 3–5 unit, dan 8,2% untuk 6+ unit. Fitur teratas menurut importance model adalah unit lulus semester kedua (34,8%), unit lulus semester pertama (19,5%), dan nilai semester kedua (15,1%). Semua perbandingan ini bersifat deskriptif, bukan bukti sebab-akibat.

**Kesimpulan:** institusi menghadapi proporsi dropout yang substansial. Capaian unit/nilai akademik dan status administrasi dapat menjadi sinyal untuk memprioritaskan peninjauan serta dukungan siswa. Prototipe menunjukkan baseline yang menjanjikan, tetapi menggunakan fitur hingga semester kedua; karena itu hasilnya belum merupakan sistem peringatan dini sebelum semester berjalan selesai. Validasi pada kohort baru, pemeriksaan fairness, dan evaluasi dampak intervensi diperlukan sebelum pemakaian operasional.

### Rekomendasi Action Items
- Jadwalkan konsultasi akademik bagi siswa dengan jumlah unit lulus atau nilai yang menurun/rendah, dan catat tindak lanjutnya.
- Tawarkan rujukan ke layanan keuangan bagi siswa yang memiliki tunggakan atau status pembayaran belum aktif; hindari menganggap status administrasi sebagai bukti penyebab dropout.
- Uji model secara prospektif pada kohort berikutnya dan ukur recall, precision, kalibrasi, serta performa per kelompok sebelum menentukan ambang intervensi.
- Audit potensi bias berdasarkan gender, usia, dan kelompok relevan lainnya; batasi akses data siswa dan jangan gunakan prediksi sebagai dasar sanksi atau keputusan akademik otomatis.
- Bangun pencatatan ID pseudonim dan snapshot semester berkala agar institusi dapat memantau perkembangan, tren, dan dampak program dukungan.
