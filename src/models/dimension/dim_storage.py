
from models.base import Base
from sqlalchemy import BigInteger, ForeignKey, SmallInteger, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column


class DimStorage(Base):
    __tablename__ = "dim_storage"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fk_deployment_mode: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_deployment_mode.id"))
    fk_region: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_region.id"))
    fk_type: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_storage_type.id"))
    name: Mapped[str] = mapped_column(String)