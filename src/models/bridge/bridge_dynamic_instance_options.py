from sqlalchemy import (
    ForeignKey,
    Identity,
    Integer,
    SmallInteger,
    String,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from models.base import Base


class BridgeDynamicInstanceOption(Base):
    __tablename__ = "bridge_dynamic_instance_options"

    fk_instance: Mapped[int] = mapped_column(
        Integer, ForeignKey("fact_current_dynamic_compute.id"), primary_key=True
    )
    fk_option: Mapped[int] = mapped_column(
        Integer, ForeignKey("fact_current_instance_instance_option.id", primary_key=True)
    )
