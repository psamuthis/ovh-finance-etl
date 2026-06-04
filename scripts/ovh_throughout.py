import json
from typing import Any
import ovh
from dotenv import load_dotenv
import os

from src.connector.ovh_connection import OVHConnector

load_dotenv()

ovh_client: ovh.Client = OVHConnector._get_client()

with open("sample-api-response/kubernetes/b41-throughout.txt", "w") as file:
    file.write("")


# api_response = ovh_client.get("/cloud/project/")
# json_response = json.dumps(api_response, indent=3)

# with open("sample-api-response/kubernetes/b41-throughout.txt", "a") as file:
# file.write(f"""\nListing ALL services\n
# endpoint=/cloud/project/\n
# \n{json_response}\n
# ---------------------------------------
# """)


service_id = "b41a8077d3ed49c69ddc77ed0b16572e"
api_response = ovh_client.get(f"/cloud/project/{service_id}")
json_response: str = json.dumps(api_response, indent=3)

with open("sample-api-response/kubernetes/b41-throughout.txt", "a") as file:
    file.write(f"""\nService {service_id} details:\n
    endpoint=/cloud/project/{service_id}\n
    {json_response}\n
    --------------------------------------
    """)

api_response = ovh_client.get(f"/cloud/project/{service_id}/kube")
cluster_ids: list[str] = api_response  # type: ignore
json_response: str = json.dumps(api_response, indent=3)

with open("sample-api-response/kubernetes/b41-throughout.txt", "a") as file:
    file.write(f"""Service {service_id} clusters:\n
    endpoint=/cloud/project/{service_id}/kube/\n
    {json_response}\n
    ---------------------------------------
    """)

for cluster_id in cluster_ids:
    api_response = ovh_client.get(f"/cloud/project/{service_id}/kube/{cluster_id}")
    json_response = json.dumps(api_response, indent=3)

    with open("sample-api-response/kubernetes/b41-throughout.txt", "a") as file:
        file.write(f"""Service {service_id} -> cluster {cluster_id} details:\n
        endpoint=/cloud/project/{service_id}/kube/{cluster_id}/\n
        {json_response}\n
        -----------------------------------------
        """)

    api_response = ovh_client.get(f"/cloud/project/{service_id}/kube/{cluster_id}/node")
    json_response = json.dumps(api_response, indent=3)

    with open("sample-api-response/kubernetes/b41-throughout.txt", "a") as file:
        file.write(f"""Cluster {cluster_id} node list:\n
        endpoint=/cloud/project/{service_id}/kube/{cluster_id}/node\n
        {json_response}\n
        -----------------------------------------
        """)
