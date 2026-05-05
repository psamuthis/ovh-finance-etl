from sqlalchemy import (
    BigInteger,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DimUnit(DeclarativeBase):
    __tablename__ = "dim_unit"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    unit: Mapped[str] = mapped_column(String)
    measure_type: Mapped[str] = mapped_column(String)
    standard_unit: Mapped[str] = mapped_column(String)
