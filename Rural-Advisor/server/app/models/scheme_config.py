from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SchemeConfig(Base):
    __tablename__ = 'scheme_configs'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    annual_rate: Mapped[float]
    tenure_months: Mapped[int]
