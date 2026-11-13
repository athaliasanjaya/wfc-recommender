# ==========================================
# Membuat tabel di database (aman dijalankan berulang)
# ==========================================
from sqlalchemy import inspect

from db import get_engine, metadata

engine = get_engine()
metadata.create_all(engine)  # hanya membuat tabel yang belum ada

print("Tabel di database:")
for nama in inspect(engine).get_table_names():
    print(f"  - {nama}")