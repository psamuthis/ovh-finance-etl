from typing import Generic, Protocol, Tuple, Type, TypeVar

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, Session, mapped_column

class CompositeIdModel(Protocol):
    def get_composite_id(self) -> Tuple[int, int]: ...


T = TypeVar("T", bound=CompositeIdModel)

class ServiceBridge(Generic[T]):

    def __init__(self, db: Session, model_class: Type[T]):
        self.db: Session = db
        self.model_class: Type[T] = model_class

    def insert_one(self, record: T) -> Tuple[int, int]:
        self.db.add(record)
        self.db.flush()
        return record.get_composite_id()
