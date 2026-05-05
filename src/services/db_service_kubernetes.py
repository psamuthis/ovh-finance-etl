from sqlalchemy.orm import Session

from src.models.dimension.dim_kubernetes import DimKubernetes


class DBServiceKubernetes:

    def __init__(self, db: Session):
        self.db: Session = db

    def insert_one(self, dim_kube: DimKubernetes) -> int:
        self.db.add(dim_kube)
        self.db.flush()
        return dim_kube.id
