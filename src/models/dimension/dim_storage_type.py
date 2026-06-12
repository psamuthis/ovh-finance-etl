from sqlalchemy import (
    BigInteger,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from models.base import Base


class DimStorageType(Base):
    __tablename__ = "dim_storage_type"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    type: Mapped[str] = mapped_column(String)
