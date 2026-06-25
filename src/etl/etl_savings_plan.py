from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
import re
from typing import Any
from config import DECIMAL_PRECISION
from dateutil import parser

from connector.postgres_connection import WarehouseSessionLocal
from etl.dataclass.shared import Quantity
from models.bridge.bridge_over_quota_savings_plan import BridgeOverQuotaSavingsPlan
from models.dimension.dim_savings_plan import DimSavingsPlan
from models.fact.fact_savings_plan_over_quota import FactSavingsPlanOverQuota
from services.bridge.service_bridge_savings_quota import ServiceBridge
from services.db_service import DBService
from services.dimension.service_time import ServiceTime
from services.dimension.service_unit import ServiceUnit
from services.fact.service_over_quota import OVER_QUOTA_TOK, ServiceOverQuota
from services.dimension.service_savings_plan import ServiceSavingsPlan

@dataclass
class SavingsPlanEntry:
    size: int
    period_from: datetime
    period_to: datetime
    flavor: str
    name: str
    currency_code: str
    price: Decimal

@dataclass
class OverQuotaEntry:
    flavor: str
    savings_plan_ids: list[str]
    quantity: Quantity
    price: Decimal

class ETLSavingsPlan:
    def __init__(self, service_id: str, archived_at: datetime):
        self.service_id: str = service_id
        self.savings_plan: dict[str, SavingsPlanEntry] = {}
        self.archived_at: datetime = archived_at
        self.over_quota: list[OverQuotaEntry] = []

    def extract_data(self, savings_plan_data: list[dict[str, Any]], over_quota_data: list[dict[str, Any]]) -> None:
        for flavor_group in savings_plan_data:
            for details in flavor_group["details"]:
                self.savings_plan[details["id"]] = SavingsPlanEntry(
                    details["size"],
                    parser.parse(details["period"]["from"]),
                    parser.parse(details["period"]["to"]),
                    flavor_group["flavor"],
                    details["planName"],
                    details["totalPrice"]["currencyCode"],
                    Decimal(details["totalPrice"]["value"])
                )

        self.extract_over_quota(over_quota_data)

    def extract_over_quota(self, over_quota_data: list[dict[str, Any]]) -> None:
        for instance_group in over_quota_data:
            if "savingsPlanIds" not in instance_group:
                continue

            self.over_quota.append(OverQuotaEntry(
                instance_group["reference"].replace(OVER_QUOTA_TOK, ""),
                instance_group["savingsPlanIds"],
                Quantity(instance_group["quantity"]["unit"], Decimal(instance_group["quantity"]["value"])),
                instance_group["totalPrice"]
            ))

    def load_data(self) -> None:
        with WarehouseSessionLocal() as db:
            for over_quota in self.over_quota:
                fk_over_quota: int = ServiceOverQuota(db).insert_one(FactSavingsPlanOverQuota(
                    fk_unit=ServiceUnit(db).get_or_create(over_quota.quantity.unit),
                    fk_created_at=ServiceTime(db).get_or_create(self.archived_at),
                    value=over_quota.quantity.value,
                    price=over_quota.price,
                    flavor=over_quota.flavor
                ))

                for id in over_quota.savings_plan_ids:
                    if id not in self.savings_plan:
                        continue

                    fk_savings_plan: int = ServiceSavingsPlan(db).get_or_create(
                        DimSavingsPlan(
                            name=self.savings_plan[id].name,
                            fk_period_from=ServiceTime(db).get_or_create(self.savings_plan[id].period_from),
                            fk_period_to=ServiceTime(db).get_or_create(self.savings_plan[id].period_to),
                            size=self.savings_plan[id].size,
                            flavor=over_quota.flavor,
                            currency_code=self.savings_plan[id].currency_code,
                            price=round(self.savings_plan[id].price, DECIMAL_PRECISION),
                            plan_id=id),
                        self.savings_plan[id].period_from,
                        self.savings_plan[id].period_to
                    )

                    ServiceBridge(db, BridgeOverQuotaSavingsPlan).insert_one(BridgeOverQuotaSavingsPlan(
                        fk_savings_plan=fk_savings_plan,
                        fk_over_quota=fk_over_quota
                    ))

                db.commit()

                    


            