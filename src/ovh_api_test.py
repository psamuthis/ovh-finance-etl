import json
from typing import Any
import ovh
from dotenv import load_dotenv
import os

from connector.ovh_connection import OVHConnector
from services.service_kubernetes import ServiceKubernetes

load_dotenv()

ovh_client: ovh.Client = OVHConnector._get_client()

# with open("sample-api-response/kubernetes/throughout.txt", "w") as file:
# file.write("")


# api_response = ovh_client.get("/cloud/project/")
# json_response = json.dumps(api_response, indent=3)

# with open("sample-api-response/kubernetes/throughout.txt", "a") as file:
# file.write(f"""\nListing ALL services\n
# endpoint=/cloud/project/\n
# \n{json_response}\n
# ---------------------------------------
# """)


service_id = "b41a8077d3ed49c69ddc77ed0b16572e"
# api_response = ovh_client.get(f"/cloud/project/{service_id}")
# json_response: str = json.dumps(api_response, indent=3)

# with open("sample-api-response/kubernetes/throughout.txt", "a") as file:
# file.write(f"""\nService {service_id} details:\n
# endpoint=/cloud/project/{service_id}\n
# {json_response}\n
# --------------------------------------
# """)

# api_response = ovh_client.get(f"/cloud/project/{service_id}/kube")
# json_response: str = json.dumps(api_response, indent=3)

# with open("sample-api-response/kubernetes/throughout.txt", "a") as file:
# file.write(f"""Service {service_id} clusters:\n
# endpoint=/cloud/project/{service_id}/kube/\n
# {json_response}\n
# ---------------------------------------
# """)

cluster_id = "8c8d289c-c36e-4d64-bf63-448ac34dfcd1"
# api_response = ovh_client.get(f"/cloud/project/{service_id}/kube/{cluster_id}")
# json_response = json.dumps(api_response, indent=3)

# with open("sample-api-response/kubernetes/throughout.txt", "a") as file:
# file.write(f"""Service {service_id} -> cluster {cluster_id} details:\n
# endpoint=/cloud/project/{service_id}/kube/{cluster_id}/\n
# {json_response}\n
# -----------------------------------------
# """)


# api_response = ovh_client.get(f"/cloud/project/{service_id}/kube/{cluster_id}/node")
# json_response = json.dumps(api_response, indent=3)

# with open("sample-api-response/kubernetes/throughout.txt", "a") as file:
# file.write(f"""Cluster {cluster_id} node list:\n
# endpoint=/cloud/project/{service_id}/kube/{cluster_id}/node\n
# {json_response}\n
# -----------------------------------------
# """)


# node_id = "247e334d-e329-4f69-ae11-a60cf0c86907"
# api_response = ovh_client.get(
# f"/cloud/project/{service_id}/kube/{cluster_id}/node/{node_id}"
# )
# json_response = json.dumps(api_response, indent=3)

# with open("sample-api-response/kubernetes/throughout.txt", "a") as file:
# file.write(f"""Cluster {cluster_id} -> node {node_id} details:\n
# endpoint=/cloud/project/{service_id}/kube/{cluster_id}/node/{node_id}\n
# {json_response}\n
# -----------------------------------------
# """)


# cluster: str | None = ServiceKubernetes.get_node_cluster(
# "b41a8077d3ed49c69ddc77ed0b16572e", "247e334d-e329-4f69-ae11-a60cf0c86907"
# )

# print(cluster)

service: ServiceKubernetes = ServiceKubernetes(service_id)
service.list_clusters(service)
