# Redis Weather Cache - Setup Guide

Ikuti langkah-langkah ini untuk menjalankan program caching Redis di laptop Anda:

## 1. Clone Repository

Buka terminal dan jalankan:

```bash
git clone <URL_GITHUB_KITA>
cd <NAMA_FOLDER_REPO>
```

## 2. Install Library Python

Pastikan terminal sudah terbuka di dalam folder proyek, lalu jalankan:

```bash
pip install fastapi uvicorn redis python-dotenv
```

## 3. Setup Akun & Token Redis (.env)

Karena kita menggunakan cloud database (Upstash), kita perlu memasukkan kredensial. Masing-masing harus membuat database sendiri:

1. Buka website [upstash.com](https://upstash.com) dan login menggunakan akun Google atau GitHub
2. Klik tombol **Create Database**, isi nama database (contoh: tugas-redis), pilih tipe **Redis**, dan pilih Region **Singapore**
3. Setelah database berhasil dibuat, scroll ke bawah untuk mencari kredensial Anda (Endpoint/Host, Port, dan Password)
4. Buka folder proyek dan buat file baru bernama `.env` di sebelah file `main.py`
5. Salin format dari file `.env.example` dan tempel ke file `.env`
6. Isi nilai Host, Port, dan Password dengan data dari dashboard Upstash Anda

## 4. Jalankan Server

```bash
uvicorn main:app --reload
```

## 5. Cara Menguji Aplikasi

1. Buka browser ke: `http://127.0.0.1:8000/cuaca/makassar`
2. Pada akses pertama kali (Cache Miss), akan terasa delay sekitar 2 detik
3. Langsung tekan refresh browser dalam waktu kurang dari 1 menit (Cache Hit), dan respons akan langsung instan (~0.1 detik)
4. Periksa log di terminal untuk melihat perbedaan waktu eksekusinya

## 6. Update ke GitHub

Jalankan tiga perintah berikut di terminal untuk mengunggah perubahan ke GitHub:

```bash
git add README.md
git commit -m "docs: ubah instruksi setup upstash mandiri untuk kelompok"
git push origin main
```