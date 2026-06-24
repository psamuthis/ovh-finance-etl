from dataclasses import dataclass, field
from decimal import Decimal

from etl.dataclass.shared import Quantity


@dataclass
class VolumeDetails:
    quantity: Quantity
    resource_id: str
    total_price: Decimal
    volume_uuid: str


@dataclass
class Volume:
    deployment_mode: str = ""
    details: list[VolumeDetails] = field(default_factory=list)
    region: str = ""
    type: str = ""
