# server/test_create_tables.py

from app.core.database import Base, engine
from app.models import user, report

print("Tables known to Base before create_all:", Base.metadata.tables.keys())

Base.metadata.create_all(bind=engine)

print("✅ create_all() executed without error")