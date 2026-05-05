from sqlalchemy import (
    BigInteger,
    String,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class DimDeploymentMode(DeclarativeBase):
    __tablename__ = "dim_deployment_mode"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)
