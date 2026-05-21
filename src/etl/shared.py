from dataclasses import dataclass


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
