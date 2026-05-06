from sqlalchemy import (
    BigInteger,
    SmallInteger,
    ForeignKey,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from models.base import Base


class DimVolume(Base):
    __tablename__ = "dim_volume"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    volume_uuid: Mapped[str] = mapped_column(Uuid)
    deployment_mode_fk: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("dim_deployment_mode")
    )
    region_fk: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_region.id"))
    type_fk: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("dim_storage_type.id")
    )
