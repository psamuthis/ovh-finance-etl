from sqlalchemy.orm import Session

from models.dimension.dim_volume import DimVolume


class ServiceVolume:

    def __init__(self, db: Session):
        self.db: Session = db

    def insert_one(self, volume: DimVolume) -> int:
        self.db.add(volume)
        self.db.flush()
        return volume.id
