from sqlalchemy import (
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from models.base import Base


class BridgeFixedInstanceOption(Base):
    __tablename__ = "bridge_fixed_instance_options"

    fk_instance: Mapped[int] = mapped_column(
        Integer, ForeignKey("fact_current_fixed_compute.id"), primary_key=True
    )
    fk_option: Mapped[int] = mapped_column(
        Integer, ForeignKey("fact_current_instance_instance_option.id"), primary_key=True
    )
