from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from etl.dataclass.instance import Bandwidth
from etl.dataclass.shared import Quantity


@dataclass
class StorageEntry:
    incoming_bandwidth: Bandwidth
    incoming_internal_bandwidth: Bandwidth
    outgoing_bandwidth: Bandwidth
    outgoing_internal_bandwidth: Bandwidth
    retrieval_fees_quantity: Quantity
    stored_quantity: Quantity
    name: Optional[str] = ""
    type: str = ""
    deployment_mode: str = ""
    region: str = ""
    retrieval_fees_price: Decimal = Decimal(0)
    stored_price: Decimal = Decimal(0)