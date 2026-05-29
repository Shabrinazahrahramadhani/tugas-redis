import time
import json
import redis
import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Load environment variables dari .env file
load_dotenv()

app = FastAPI()

# --- 1. Inisialisasi Koneksi Redis (Upstash) ---
try:
    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")
    redis_password = os.getenv("REDIS_PASSWORD")
    
    if not all([redis_host, redis_port, redis_password]):
        raise ValueError("Environment variables REDIS_HOST, REDIS_PORT, dan REDIS_PASSWORD harus diisi di file .env")
    
    redis_client = redis.Redis(
        host=redis_host,
        port=int(redis_port),
        username="default",
        password=redis_password,
        decode_responses=True,
        ssl=True
    )
    # Test koneksi
    redis_client.ping()
    print("[LOG] Koneksi Redis berhasil!")

    # Debug: cek apakah bisa SET dan GET
    redis_client.set("test_key", "test_value", ex=10)
    test_val = redis_client.get("test_key")
    if test_val == "test_value":
        print("[LOG] Redis SET/GET test: BERHASIL ✅")
    else:
        print("[LOG] Redis SET/GET test: GAGAL ❌ - cek credentials")

except ValueError as e:
    print(f"[ERROR] Konfigurasi invalid: {e}")
    raise
except redis.exceptions.AuthenticationError as e:
    print(f"[ERROR] Username atau Password Redis salah. Periksa credentials di Upstash Dashboard")
    print(f"        Error detail: {e}")
    raise
except Exception as e:
    print(f"[ERROR] Gagal terhubung ke Redis: {e}")
    raise

# --- 2. Database Dummy (In-Memory Dictionary) ---
dummy_db = {
    "makassar": {"suhu": 32, "kondisi": "Cerah", "kelembapan": "70%"},
    "jakarta": {"suhu": 34, "kondisi": "Berawan", "kelembapan": "80%"},
    "bandung": {"suhu": 24, "kondisi": "Hujan Ringan", "kelembapan": "85%"}
}

def fetch_from_dummy_db(kota: str):
    """Simulasi query lambat ke database utama."""
    time.sleep(2)  # Delay 2 detik untuk simulasi lambatnya query ke database
    return dummy_db.get(kota.lower())

# --- 3. Endpoint API (Implementasi Cache-Aside) ---
@app.get("/cuaca/{kota}")
def get_cuaca(kota: str):
    start_time = time.time()
    cache_key = f"cuaca:{kota.lower()}"

    try:
        # Langkah A: Cek data di Redis terlebih dahulu
        cached_data = redis_client.get(cache_key)

        if cached_data:
            # [CACHE HIT] Data ditemukan di Redis
            process_time = time.time() - start_time
            print(f"[LOG] CACHE HIT! Data '{kota}' diambil dari Redis. Waktu eksekusi: {process_time:.4f} detik")
            
            return {
                "status": "success",
                "sumber_data": "Cache (Redis Upstash)",
                "waktu_respons": f"{process_time:.4f} detik",
                "data": json.loads(cached_data)
            }
        
        # Langkah B: [CACHE MISS] Data tidak ada di Redis, ambil dari Database
        db_data = fetch_from_dummy_db(kota)
        
        if not db_data:
            raise HTTPException(status_code=404, detail="Kota tidak ditemukan di database dummy")

        # Langkah C: Simpan data dari database ke Redis dengan TTL 60 detik (EX 60)
        result = redis_client.set(cache_key, json.dumps(db_data), ex=60)
        print(f"[LOG] Redis SET result: {result}")  # Harus muncul: True

        process_time = time.time() - start_time
        print(f"[LOG] CACHE MISS! Data '{kota}' diambil dari Database (Delay 2s). Waktu eksekusi: {process_time:.4f} detik")
        
        return {
            "status": "success",
            "sumber_data": "Database Dummy",
            "waktu_respons": f"{process_time:.4f} detik",
            "data": db_data
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Kesalahan saat mengakses data: {e}")
        raise HTTPException(status_code=500, detail=f"Kesalahan server: {str(e)}")