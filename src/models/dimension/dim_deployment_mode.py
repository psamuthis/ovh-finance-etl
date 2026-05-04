from typing import Optional, ClassVar
from sqlalchemy import (
    BigInteger,
    String,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    declarative_base,
    mapped_column,
)

from src.connector.postgres_connection import WarehouseSessionLocal


class DimDeploymentMode(DeclarativeBase):
    __tablename__ = "dim_deployment_mode"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    _cache: ClassVar[dict[str, int]] = {}
    _cache_loaded: ClassVar[bool] = False

    @staticmethod
    def get_all(db: Session) -> list["DimDeploymentMode"]:
        return db.query(DimDeploymentMode).all()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional["DimDeploymentMode"]:
        return db.query(DimDeploymentMode).filter_by(name=name).first()

    @staticmethod
    def insert_one(db: Session, name: str) -> int:
        dep_mode: DimDeploymentMode = DimDeploymentMode(name=name)
        db.add(dep_mode)
        db.flush()
        DimDeploymentMode._cache[name] = dep_mode.id
        return dep_mode.id

    @staticmethod
    def get_or_create(db: Session, dep_name: str) -> int:
        DimDeploymentMode._load_cache(db)

        if dep_name in DimDeploymentMode._cache:
            return DimDeploymentMode._cache[dep_name]

        new_id: int = DimDeploymentMode.insert_one(db, dep_name)
        DimDeploymentMode._cache[dep_name] = new_id
        return new_id

    @staticmethod
    def _load_cache(db: Session) -> None:
        if DimDeploymentMode._cache_loaded:
            return

        dep_modes: list[DimDeploymentMode] = DimDeploymentMode.get_all(db)
        DimDeploymentMode._cache = {mode.name: mode.id for mode in dep_modes}
        DimDeploymentMode._cache_loaded = True

    @staticmethod
    def _refresh_cache(db: Session) -> None:
        DimDeploymentMode._cache_loaded = False
        DimDeploymentMode._load_cache(db)
