import json

import ovh

from connector.ovh_connection import OVHConnector

ovh_client: ovh.Client = OVHConnector._get_client()

service_id: str = "b41a8077d3ed49c69ddc77ed0b16572e"
history_usage = ovh_client.get(f"/cloud/project/{service_id}/usage/history")

if history_usage is None:
    exit(0)

with open("sample-api-response/history_example.json", "w") as file:
    json.dump(history_usage, file, indent=3)


for run in history_usage:
    run_id: str = run["id"]
    details = ovh_client.get(f"/cloud/project/{service_id}/usage/history/{run_id}")

    with open("sample-api-response/history_example.json", "a") as file:
        json.dump(details, file, indent=3)
