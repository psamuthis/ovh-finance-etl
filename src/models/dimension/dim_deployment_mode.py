from sqlalchemy import (
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


class DimDeploymentMode(Base):
    __tablename__ = "dim_deployment_mode"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
