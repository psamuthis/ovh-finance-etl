from sqlalchemy.orm import Session

from models.fact import fact_current_dynamic_compute


class ServiceInstance:
    def __init__(self, db: Session):
        self.db: Session = db
