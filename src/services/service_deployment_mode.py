from typing import ClassVar, Optional

from sqlalchemy.orm import Session

from models.dimension.dim_deployment_mode import DimDeploymentMode


class ServiceDeploymentMode:
    _cache: ClassVar[dict[str, int]] = {}
    _cache_loaded: ClassVar[bool] = False

    def __init__(self, db: Session):
        self.db: Session = db

        if not ServiceDeploymentMode._cache_loaded:
            self._load_cache()

    def get_all(self) -> list[DimDeploymentMode]:
        return self.db.query(DimDeploymentMode).all()

    def get_by_name(self, name: str) -> Optional["DimDeploymentMode"]:
        return self.db.query(DimDeploymentMode).filter_by(name=name).first()

    def insert_one(self, name: str) -> int:
        dep_mode: DimDeploymentMode = DimDeploymentMode(name=name)
        self.db.add(dep_mode)
        self.db.flush()
        ServiceDeploymentMode._cache[name] = dep_mode.id
        return dep_mode.id

    def get_or_create(self, dep_name: str) -> int:
        self._load_cache()

        if dep_name in ServiceDeploymentMode._cache:
            return ServiceDeploymentMode._cache[dep_name]

        new_id: int = self.insert_one(dep_name)
        ServiceDeploymentMode._cache[dep_name] = new_id
        return new_id

    def _load_cache(self) -> None:
        if ServiceDeploymentMode._cache_loaded:
            return

        dep_modes: list[DimDeploymentMode] = self.get_all()
        ServiceDeploymentMode._cache = {mode.name: mode.id for mode in dep_modes}
        ServiceDeploymentMode._cache_loaded = True

    def _refresh_cache(self) -> None:
        ServiceDeploymentMode._cache_loaded = False
        self._load_cache()
