from datetime import datetime
from typing import Type, TypeVar, Generic
from sqlalchemy.orm import Mapped, Session, mapped_column

from models.base import Base
from models.dimension.dim_time import DimTime


class HasIdModel(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)


T = TypeVar("T", bound=HasIdModel)


class DIMDBService(Generic[T]):
    def __init__(self, db: Session, model_class: Type[T]):
        self.db: Session = db
        self.model_class: Type[T] = model_class

    def get_all(self) -> list[T]:
        return self.db.query(self.model_class).all()

    def insert_one(self, record: T) -> int:
        self.db.add(record)
        self.db.flush()
        return record.id
