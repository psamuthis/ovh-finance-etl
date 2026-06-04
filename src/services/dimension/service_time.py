from datetime import datetime

from sqlalchemy.orm import Session

from models.dimension.dim_time import DimTime


class ServiceTime:

    def __init__(self, db: Session):
        self.db: Session = db

    @classmethod
    def parse_iso_date(cls, date_str: str) -> datetime:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))

    def get_or_create(self, timestamp: datetime) -> int:
        existing_record: DimTime | None = (
            self.db.query(DimTime).filter_by(timestamptz=timestamp).first()
        )

        if existing_record is None:
            new_record: DimTime = DimTime(
                timestamptz=timestamp,
                year=timestamp.year,
                month=timestamp.month,
                day=timestamp.day,
                quarter=(timestamp.month - 1) // 3 + 1,
            )
            self.db.add(new_record)
            self.db.flush()
            return new_record.id

        return existing_record.id
