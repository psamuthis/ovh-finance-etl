from dataclasses import dataclass


@dataclass
class Quantity:
    unit: str
    value: float


@dataclass
class TotalPrice:
    currency_code: str
    ucents_price: float
    text_value: str
    value: float
