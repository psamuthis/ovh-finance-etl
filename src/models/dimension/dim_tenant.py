from sqlalchemy import (
    BigInteger,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class DimTenant(Base):
    __tablename__ = "dim_tenant"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    project_id: Mapped[str] = mapped_column(String)
