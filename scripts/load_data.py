# ==========================================
# Memuat data bersih (CSV) ke tabel coffee_shop dan review
# Aman dijalankan berulang: hanya menambah data yang belum ada.
# ==========================================
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import get_engine

BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed"

engine = get_engine()

# ==========================================
# 1. Baca CSV
# ==========================================
places = pd.read_csv(PROC / "places_clean.csv")
reviews = pd.read_csv(PROC / "reviews_clean.csv")

fas_path = PROC / "place_facilities.csv"
if fas_path.exists():
    fas = pd.read_csv(fas_path)[["place_id", "toilet", "tag_cocok_laptop", "additional_info_json"]]
    places = places.merge(fas, on="place_id", how="left")
else:
    print("Catatan: place_facilities.csv tidak ditemukan, kolom fasilitas dikosongkan.")
    for kolom in ["toilet", "tag_cocok_laptop", "additional_info_json"]:
        places[kolom] = None

# ==========================================
# 2. Siapkan tabel coffee_shop
# ==========================================
coffee_shop = (
    places
    .rename(columns={
        "name": "nama_coffee_shop",
        "category": "kategori_google",
        "address": "alamat",
        "neighborhood": "wilayah",
        "google_score": "skor_google",
        "google_reviews_count": "jumlah_ulasan_google",
        "maps_url": "url_maps",
        "additional_info_json": "info_google_json",
    })
    .loc[:, [
        "place_id", "nama_coffee_shop", "kategori_google", "alamat", "wilayah",
        "lat", "lng", "skor_google", "jumlah_ulasan_google", "url_maps",
        "toilet", "tag_cocok_laptop", "info_google_json",
    ]]
)

with engine.begin() as conn:
    ada = set(pd.read_sql(text("SELECT place_id FROM coffee_shop"), conn)["place_id"])
    baru = coffee_shop[~coffee_shop["place_id"].isin(ada)]
    if len(baru):
        baru.to_sql("coffee_shop", conn, if_exists="append", index=False)
    print(f"coffee_shop : +{len(baru)} baris baru")

    # ==========================================
    # 3. Siapkan tabel review
    # ==========================================
    peta = pd.read_sql(text("SELECT id_coffee_shop, place_id FROM coffee_shop"), conn)
    review = reviews.merge(peta, on="place_id", how="left")

    tanpa_tempat = review["id_coffee_shop"].isna().sum()
    if tanpa_tempat:
        print(f"PERINGATAN: {tanpa_tempat} ulasan tidak punya tempat di coffee_shop, dilewati.")
        review = review[review["id_coffee_shop"].notna()]

    review["published_at"] = (
        pd.to_datetime(review["published_at"], utc=True)
        .dt.tz_convert(None)  # simpan sebagai waktu UTC tanpa zona
    )
    for kolom in ["stars", "rating_food", "rating_service", "rating_atmosphere", "likes"]:
        review[kolom] = review[kolom].astype("Int64")

    review = (
        review
        .rename(columns={
            "review_id": "review_id_google",
            "text_original": "teks_asli",
            "text_translated": "teks_terjemahan",
            "language": "bahasa",
            "stars": "bintang",
            "rating_food": "rating_makanan",
            "rating_service": "rating_layanan",
            "rating_atmosphere": "rating_suasana",
            "published_at": "tanggal_ulasan",
            "likes": "jumlah_like",
        })
        .loc[:, [
            "review_id_google", "id_coffee_shop", "teks_asli", "teks_terjemahan",
            "bahasa", "ada_teks", "bintang", "rating_makanan", "rating_layanan",
            "rating_suasana", "noise_level", "noise_kategori", "tanggal_ulasan",
            "jumlah_like",
        ]]
    )

    ada_r = set(pd.read_sql(text("SELECT review_id_google FROM review"), conn)["review_id_google"])
    baru_r = review[~review["review_id_google"].isin(ada_r)]
    if len(baru_r):
        baru_r.to_sql("review", conn, if_exists="append", index=False, chunksize=100)
    print(f"review      : +{len(baru_r)} baris baru")

    # ==========================================
    # 4. Ringkasan isi tabel
    # ==========================================
    print("-" * 40)
    print("Total coffee_shop :", conn.execute(text("SELECT COUNT(*) FROM coffee_shop")).scalar())
    print("Total review      :", conn.execute(text("SELECT COUNT(*) FROM review")).scalar())
    print("Ulasan per tempat :")
    hasil = conn.execute(text(
        "SELECT c.nama_coffee_shop, COUNT(*) AS jumlah "
        "FROM review r JOIN coffee_shop c ON r.id_coffee_shop = c.id_coffee_shop "
        "GROUP BY c.nama_coffee_shop ORDER BY c.nama_coffee_shop"
    ))
    for nama, jumlah in hasil:
        print(f"  {nama:30s} {jumlah}")