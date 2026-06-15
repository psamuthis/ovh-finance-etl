"""
Temporary script to retrieve and feed the raw ovh financial database
"""

from typing import Any, Optional
import ovh
from datetime import datetime, timezone
from services.dimension.api_service_kubernetes import APIServiceKubernetes
from sqlalchemy.orm import Session

from connector.ovh_connection import OVHConnector
from connector.postgres_connection import RawSessionLocal
from models.raw.current_usage_raw import CurrentUsageRaw

ENDPOINT_PREFIX: str = "/cloud/project/"
ENDPOINT_SUFFIX: str = "/usage/current"
SERVICE_ID: str = "b41a8077d3ed49c69ddc77ed0b16572e"

ovh_client: ovh.Client = OVHConnector._get_client()
service_list: Optional[list[str]] = ovh_client.get(f"{ENDPOINT_PREFIX}")

if service_list is None:
    print("Could not retrieve project IDs :(")
    exit(0)

db: Session = RawSessionLocal()

for service_id in service_list:

    call_timestamp: datetime = datetime.now(timezone.utc)
    api_response: dict[str, Any] | None = ovh_client.get(
        f"{ENDPOINT_PREFIX}{service_id}{ENDPOINT_SUFFIX}"
    )

    if api_response is None:
        raise ValueError(
            f"No response return from API at {ENDPOINT_PREFIX} + {SERVICE_ID} + {ENDPOINT_SUFFIX}"
        )

    data: dict[str, Any] = {
        "service_id": service_id,
        "period_from": api_response["period"]["from"],
        "period_to": api_response["period"]["to"],
        "call_timestamp": datetime.now(timezone.utc),
        "last_update": api_response["lastUpdate"],
        "total_price": api_response["totalPrice"]["value"],
        "total_price_currency": api_response["totalPrice"]["currencyCode"],
        "full_response_json": api_response,
        "created_at": datetime.now(timezone.utc),
    }


    current_usage_record = CurrentUsageRaw(**data)
    db.add(current_usage_record)

db.commit()
db.close()
