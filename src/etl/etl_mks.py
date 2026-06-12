from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class MKSEntries:
    deployment_mode: str

class ETLMKS:
    def __init__(self, service_id: str, period_from: datetime, period_to: datetime):
        self.service_id: str = service_id
        self.period_from: datetime = period_from
        self.period_to: datetime = period_to
        # self.mks_entries: list[MKSEntries] = []
