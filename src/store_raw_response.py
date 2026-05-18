"""
Temporary script to retrieve and feed the raw ovh financial database
"""

from typing import Any
import ovh
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from connector.ovh_connection import OVHConnector
from connector.postgres_connection import RawSessionLocal
from models.raw.current_usage_raw import CurrentUsageRaw

ENDPOINT_PREFIX: str = "/cloud/project/"
ENDPOINT_SUFFIX: str = "/usage/current"
SERVICE_ID: str = "b41a8077d3ed49c69ddc77ed0b16572e"

ovh_client: ovh.Client = OVHConnector._get_client()

call_timestamp: datetime = datetime.now(timezone.utc)
api_response: dict[str, Any] | None = ovh_client.get(
    f"{ENDPOINT_PREFIX}{SERVICE_ID}{ENDPOINT_SUFFIX}"
)

if api_response is None:
    raise ValueError(
        f"No response return from API at {ENDPOINT_PREFIX} + {SERVICE_ID} + {ENDPOINT_SUFFIX}"
    )

data: dict[str, Any] = {
    "service_id": SERVICE_ID,
    "period_from": api_response["period"]["from"],
    "period_to": api_response["period"]["to"],
    # "call_timestamp": call_timestamp,
    "call_timestamp": datetime.now(timezone.utc),
    "last_update": api_response["lastUpdate"],
    "total_price": api_response["totalPrice"]["value"],
    "total_price_currency": api_response["totalPrice"]["currencyCode"],
    "full_response_json": api_response,
    "created_at": datetime.now(timezone.utc),
}


db: Session = RawSessionLocal()
current_usage_record = CurrentUsageRaw(**data)
db.add(current_usage_record)
db.commit()
print("Record inserted.")

db.close()
