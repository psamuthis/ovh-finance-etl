import sys
import os
import json
from typing import Any
import ovh

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.connector.ovh_connection import OVHConnector
from src.services.dimension.api_service_kubernetes import APIServiceKubernetes

ovh_client: ovh.Client = OVHConnector._get_client()
tenants: list[str] = APIServiceKubernetes.list_services()
all_clusters: dict[str, list[str]] = {}
all_nodes: dict[str, list[dict[str, Any]]] = {}

for tenant in tenants:
    all_clusters[tenant] = APIServiceKubernetes(tenant).list_clusters()

for tenant in all_clusters:
    for cluster in all_clusters[tenant]:
        all_nodes[cluster] = APIServiceKubernetes(tenant).list_cluster_nodes(cluster)

with open("sample-api-response/kubernetes/all_nodes.json", "w") as file:
    json.dump(all_nodes, file, indent=3)
