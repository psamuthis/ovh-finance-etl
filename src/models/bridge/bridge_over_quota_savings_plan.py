from typing import Tuple

from models.base import Base
from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column


class BridgeOverQuotaSavingsPlan(Base):
    __tablename__ = "bridge_over_quota_savings_plan"

    fk_savings_plan: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fk_over_quota: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    def get_composite_id(self) -> Tuple[int, int]:
        return (self.fk_savings_plan, self.fk_over_quota)