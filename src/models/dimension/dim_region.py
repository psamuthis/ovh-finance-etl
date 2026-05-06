from sqlalchemy import (
    BigInteger,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.base import Base


class DimRegion(Base):
    __tablename__ = "dim_region"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)
