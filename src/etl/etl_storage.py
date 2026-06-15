from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from tkinter import W
from typing import Any

from connector.postgres_connection import WarehouseSessionLocal
from etl.dataclass.instance import Bandwidth
from etl.dataclass.shared import Quantity
from models.dimension.dim_storage import DimStorage
from models.fact.fact_storage import FactCurrentStorage
from services.db_service import DBService
from services.dimension.service_deployment_mode import ServiceDeploymentMode
from services.dimension.service_region import ServiceRegion
from services.dimension.service_storage_type import ServiceStorageType
from services.dimension.service_time import ServiceTime
from services.dimension.service_unit import ServiceUnit

@dataclass
class StorageEntry:
    name: str
    type: str
    deployment_mode: str
    region: str
    incoming_bandwidth: Bandwidth
    incoming_internal_bandwidth: Bandwidth
    outgoing_bandwidth: Bandwidth
    outgoing_internal_bandwidth: Bandwidth
    retrieval_fees_quantity: Quantity
    retrieval_fees_price: Decimal
    stored_quantity: Quantity
    stored_price: Decimal


class ETLStorage:
    def __init__(self, service_id: str, period_from: datetime, period_to: datetime):
        self.service_id: str = service_id
        self.period_from: datetime = period_from
        self.period_to: datetime = period_to
        self.storage: list[StorageEntry] = []

    def extract_data(self, storage_data: list[dict[str, Any]]) -> None:
        for storage_entry in storage_data:
            incoming_bandwidth: Bandwidth = Bandwidth(Quantity(
                    storage_entry["incomingBandwidth"]["quantity"]["unit"],
                    storage_entry["incomingBandwidth"]["quantity"]["value"]),
                storage_entry["incomingBandwidth"]["totalPrice"])

            incoming_internal_bandwidth: Bandwidth = Bandwidth(Quantity(
                    storage_entry["incomingInternalBandwidth"]["quantity"]["unit"],
                    storage_entry["incomingInternalBandwidth"]["quantity"]["value"]),
                storage_entry["incomingInternalBandwidth"]["totalPrice"])

            outgoing_bandwidth: Bandwidth = Bandwidth(Quantity(
                    storage_entry["outgoingBandwidth"]["quantity"]["unit"],
                    storage_entry["outgoingBandwidth"]["quantity"]["value"]),
                storage_entry["outgoingBandwidth"]["totalPrice"])

            outgoing_internal_bandwidth: Bandwidth = Bandwidth(Quantity(
                    storage_entry["outgoingInternalBandwidth"]["quantity"]["unit"],
                    storage_entry["outgoingInternalBandwidth"]["quantity"]["value"]),
                storage_entry["outgoingInternalBandwidth"]["totalPrice"])

            self.storage.append(StorageEntry(
                storage_entry["bucketName"],
                storage_entry["type"],
                storage_entry["deploymentMode"],
                storage_entry["region"],
                incoming_bandwidth,
                incoming_internal_bandwidth,
                outgoing_bandwidth,
                outgoing_internal_bandwidth,
                Quantity(
                    storage_entry["retrievalFees"]["quantity"]["unit"],
                    storage_entry["retrievalFees"]["quantity"]["value"]),
                storage_entry["retrievalFees"]["totalPrice"]["value"],
                Quantity(
                    storage_entry["stored"]["quantity"]["unit"], 
                    storage_entry["stored"]["quantity"]["value"]),
                storage_entry["stored"]["totalPrice"]
            ))

    def load_data(self) -> None:
        with WarehouseSessionLocal() as db:
            for storage in self.storage:
                fk_storage: int = DBService(db, DimStorage).insert_one(DimStorage(
                    fk_deployment_mode=ServiceDeploymentMode(db).get_or_create(storage.deployment_mode),
                    fk_region=ServiceRegion(db).get_or_create(storage.region),
                    fk_type=ServiceStorageType(db).get_or_create(storage.type),
                    name=storage.name,
                ))

                DBService(db, FactCurrentStorage).insert_one(FactCurrentStorage(
                    fk_storage=fk_storage,
                    fk_period_from=ServiceTime(db).get_or_create(self.period_from),
                    fk_period_to=ServiceTime(db).get_or_create(self.period_to),
                    fk_created_at=ServiceTime(db).get_or_create(datetime.now(timezone.utc)),

                    fk_in_bandwidth_unit=ServiceUnit(db).get_or_create(storage.incoming_bandwidth.quantity.unit),
                    in_bandwidth_value=storage.incoming_bandwidth.quantity.value,
                    in_bandwidth_price=storage.incoming_bandwidth.total_price,

                    fk_in_internal_bandwidth_unit=ServiceUnit(db).get_or_create(storage.incoming_internal_bandwidth.quantity.unit),
                    in_internal_bandwidth_value=storage.incoming_internal_bandwidth.quantity.value,
                    in_internal_bandwidth_price=storage.incoming_internal_bandwidth.total_price,

                    fk_out_bandwidth_unit=ServiceUnit(db).get_or_create(storage.outgoing_bandwidth.quantity.unit),
                    out_bandwidth_value=storage.outgoing_bandwidth.quantity.value,
                    out_bandwidth_price=storage.outgoing_bandwidth.total_price,

                    fk_out_internal_bandwidth_unit=ServiceUnit(db).get_or_create(storage.outgoing_internal_bandwidth.quantity.unit),
                    out_internal_bandwidth_value=storage.outgoing_internal_bandwidth.quantity.value,
                    out_internal_bandwidth_price=storage.outgoing_internal_bandwidth.total_price,

                    fk_retrieval_fees_unit=ServiceUnit(db).get_or_create(storage.retrieval_fees_quantity.unit),
                    retrieval_fees_value=storage.retrieval_fees_quantity.value,
                    retrieval_fees_price=storage.retrieval_fees_price,

                    fk_stored_unit=ServiceUnit(db).get_or_create(storage.stored_quantity.unit),
                    stored_value=storage.stored_quantity.value,
                    stored_price=storage.stored_price
                ))

            db.commit()
