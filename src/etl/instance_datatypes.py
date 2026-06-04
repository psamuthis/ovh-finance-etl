from dataclasses import dataclass, field
from datetime import datetime
import decimal

from etl.shared import Period, Quantity, TotalPrice


@dataclass
class DynamicInstanceDetails:
    instance_id: str
    quantity: Quantity
    total_price: decimal.Decimal
    resource_id: str


@dataclass
class Bandwidth:
    quantity: Quantity
    total_price: decimal.Decimal


@dataclass
class InstanceBandwidth:
    incoming: Bandwidth
    outgoing: Bandwidth


@dataclass
class InstanceOptionDetails:
    instance_id: str
    quantity: Quantity
    total_price: decimal.Decimal


@dataclass
class DynamicInstance:
    deployment_mode: str = ""
    flavor: str = ""
    region: str = ""
    details: list[DynamicInstanceDetails] = field(default_factory=list)


@dataclass
class FixedInstance:
    deployment_mode: str
    activation_date: datetime
    instance_id: str
    resource_id: str
    flavor: str
    region: str
    total_price: decimal.Decimal


@dataclass
class SavingsPlanDetails:
    id: str
    period: Period
    plan_name: str
    size: int
    total_price: TotalPrice


@dataclass
class SavingsPlan:
    details: list[SavingsPlanDetails]
    flavor: str
