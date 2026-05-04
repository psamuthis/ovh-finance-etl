from typing import ClassVar
from sqlalchemy import (
    BigInteger,
    String,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
)


class DimStorageType(DeclarativeBase):
    __tablename__ = "dim_storage_type"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    type: Mapped[str] = mapped_column(String)

    _cache: ClassVar[dict[str, int]] = {}
    _cache_loaded: ClassVar[bool] = False

    @staticmethod
    def get_all(db: Session) -> list["DimStorageType"]:
        return db.query(DimStorageType).all()

    @staticmethod
    def insert_one(db: Session, type: str) -> int:
        storage_type: DimStorageType = DimStorageType(type=type)
        db.add(storage_type)
        db.flush()
        DimStorageType._cache[type] = storage_type.id
        return storage_type.id

    @staticmethod
    def get_or_create(db: Session, type: str) -> int:
        DimStorageType._load_cache(db)

        if type in DimStorageType._cache:
            return DimStorageType._cache[type]

        new_id: int = DimStorageType.insert_one(db, type)
        DimStorageType._cache[type] = new_id
        return new_id

    @staticmethod
    def _load_cache(db: Session) -> None:
        if DimStorageType._cache_loaded:
            return

        storage_types: list[DimStorageType] = DimStorageType.get_all(db)
        DimStorageType._cache = {type.type: type.id for type in storage_types}
        DimStorageType._cache_loaded = True

    @staticmethod
    def _refresh_cache(db: Session) -> None:
        DimStorageType._cache_loaded = False
        DimStorageType._load_cache(db)
