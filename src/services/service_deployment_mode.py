from typing import ClassVar, Optional
from typing_extensions import override

from sqlalchemy.orm import Session

from models.dimension.dim_deployment_mode import DimDeploymentMode
from services.db_service import DBService


class ServiceDeploymentMode(DBService[DimDeploymentMode]):
    _cache: ClassVar[dict[str, int]] = {}
    _cache_loaded: ClassVar[bool] = False

    def __init__(self, db: Session):
        super().__init__(db, DimDeploymentMode)

        if not ServiceDeploymentMode._cache_loaded:
            self._load_cache()

    def get_by_name(self, name: str) -> Optional["DimDeploymentMode"]:
        return self.db.query(DimDeploymentMode).filter_by(name=name).first()

    @override
    def insert_one(self, record: DimDeploymentMode) -> int:
        self.db.add(record)
        self.db.flush()
        ServiceDeploymentMode._cache[record.name] = record.id
        return record.id

    def get_or_create(self, dep_name: str) -> int:
        self._load_cache()

        if dep_name in ServiceDeploymentMode._cache:
            return ServiceDeploymentMode._cache[dep_name]

        return self.insert_one(DimDeploymentMode(dep_name))

    def _load_cache(self) -> None:
        if ServiceDeploymentMode._cache_loaded:
            return

        dep_modes: list[DimDeploymentMode] = self.get_all()
        ServiceDeploymentMode._cache = {mode.name: mode.id for mode in dep_modes}
        ServiceDeploymentMode._cache_loaded = True

    def _refresh_cache(self) -> None:
        ServiceDeploymentMode._cache_loaded = False
        self._load_cache()
