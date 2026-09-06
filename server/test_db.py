# server/test_db.py

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://sihuser:sihpassword@localhost:5432/sih_rural_db"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print("✅ Connected successfully!")
        print(result.fetchone())
except Exception as e:
    print("❌ Connection failed:", e)