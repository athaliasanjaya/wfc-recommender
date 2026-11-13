# ==========================================
# Koneksi database dan definisi tabel (dipakai skrip lain)
# ==========================================
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, MetaData,
    SmallInteger, String, Table, Text, create_engine,
)
from sqlalchemy.engine import URL

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / ".env")


def get_engine():
    # URL.create supaya password dengan karakter khusus (@, ?, #) aman
    url = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME"),
        query={"charset": "utf8mb4"},
    )
    return create_engine(url)


# ==========================================
# Definisi tabel
# ==========================================
metadata = MetaData()

TABLE_OPTS = dict(
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4",
    mysql_collate="utf8mb4_unicode_ci",
)

coffee_shop = Table(
    "coffee_shop", metadata,
    Column("id_coffee_shop", Integer, primary_key=True, autoincrement=True),
    Column("place_id", String(64), nullable=False, unique=True),
    Column("nama_coffee_shop", String(150), nullable=False),
    Column("kategori_google", String(100)),
    Column("alamat", Text),
    Column("wilayah", String(150)),
    Column("lat", Float),
    Column("lng", Float),
    Column("skor_google", Float),
    Column("jumlah_ulasan_google", Integer),
    Column("url_maps", Text),
    Column("toilet", String(20)),
    Column("tag_cocok_laptop", String(20)),
    Column("info_google_json", Text),
    **TABLE_OPTS,
)

review = Table(
    "review", metadata,
    Column("id_review", Integer, primary_key=True, autoincrement=True),
    Column("review_id_google", String(150), nullable=False, unique=True),
    Column("id_coffee_shop", Integer, ForeignKey("coffee_shop.id_coffee_shop"), nullable=False),
    Column("teks_asli", Text),
    Column("teks_terjemahan", Text),
    Column("bahasa", String(10)),
    Column("ada_teks", Boolean, nullable=False),
    Column("bintang", SmallInteger),
    Column("rating_makanan", SmallInteger),
    Column("rating_layanan", SmallInteger),
    Column("rating_suasana", SmallInteger),
    Column("noise_level", String(50)),
    Column("noise_kategori", String(20)),
    Column("tanggal_ulasan", DateTime),
    Column("jumlah_like", Integer),
    **TABLE_OPTS,
)