from models.fact.fact_savings_plan_over_quota import FactSavingsPlanOverQuota
from services.db_service import DBService
from sqlalchemy.orm import Session

OVER_QUOTA_TOK: str = r".over-quota"

class ServiceOverQuota(DBService):
    def __init__(self, db: Session):
        super().__init__(db, FactSavingsPlanOverQuota)