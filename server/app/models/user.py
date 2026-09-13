# server/app/models/user.py

import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    preferred_language = Column(String, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())