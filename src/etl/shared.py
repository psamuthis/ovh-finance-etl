from dataclasses import dataclass
from datetime import datetime


@dataclass
class Period:
    period_from: datetime
    period_to: datetime


@dataclass
class Quantity:
    unit: str
    value: int


@dataclass
class TotalPrice:
    currency_code: str
    ucents_price: float
    text_value: str
    value: float
