# ==========================================
# Cek koneksi database
# ==========================================
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

# URL.create menangani karakter khusus di password (@, ?, #, dll.)
# secara otomatis, jadi tidak perlu di-encode manual.
url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    query={"charset": "utf8mb4"},
)
engine = create_engine(url)

with engine.connect() as conn:
    print(conn.execute(text("SELECT 1")).scalar())