from typing import Any, ClassVar, Optional
from typing_extensions import override

from sqlalchemy.orm import Session

from models.dimension.dim_kubernetes import DimKubernetes
from services.dimension.api_service_kubernetes import APIServiceKubernetes
from services.db_service import DBService
from services.dimension.service_time import ServiceTime
from models.dimension.dim_tenant import DimTenant


class ServiceTenant(DBService[DimTenant]):
    _cache: ClassVar[dict[str, int]] = {}
    _cache_loaded: ClassVar[bool] = False

    def __init__(self, db: Session):
        super().__init__(db, DimTenant)

        if not ServiceTenant._cache_loaded:
            self._load_cache()

    @override
    def insert_one(self, record: DimTenant) -> int:
        self.db.add(record)
        self.db.flush()
        ServiceTenant._cache[record.name] = record.id
        return record.id

    def get_or_create(self, service_id: str) -> int:
        self._load_cache()

        if service_id in ServiceTenant._cache:
            return ServiceTenant._cache[service_id]

        service_details: dict[str, Any] = APIServiceKubernetes(service_id).get_project_details()
        return self.insert_one(
            DimTenant(
                name=service_details["description"],
                project_id=service_details["project_id"],
            )
        )

    def _load_cache(self) -> None:
        if ServiceTenant._cache_loaded:
            return

        tenants: list[DimTenant] = self.get_all()
        ServiceTenant._cache = {tenant.name: tenant.id for tenant in tenants}
        ServiceTenant._cache_loaded = True

    def _refresh_cache(self) -> None:
        ServiceTenant._cache_loaded = False
        self._load_cache()
