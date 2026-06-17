from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Period:
    period_from: datetime
    period_to: datetime


@dataclass
class Quantity:
    unit: str = ""
    value: Decimal = Decimal(0)


@dataclass
class TotalPrice:
    currency_code: str
    ucents_price: float
    text_value: str
    value: float
