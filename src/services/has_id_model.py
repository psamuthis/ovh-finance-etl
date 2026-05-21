from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class HasIdModel(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
