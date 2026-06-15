import json
from tkinter import W
from typing import Any

from connector.ovh_connection import OVHConnector
import ovh
from services.dimension.api_service_kubernetes import APIServiceKubernetes

ovh_client: ovh.Client = OVHConnector()._get_client()


service_list = ovh_client.get("/cloud/project")
if service_list is None:
    exit(0)

for service_id in service_list:
    history_instance_ids: list[str] = []
    current_instance_ids: list[str] = []
    kube_node_ids: list[str] = []

    print(f"{service_id}")

    kube_clusters: list[str] = APIServiceKubernetes(service_id).list_clusters()

    for cluster_id in kube_clusters:
        for kube_node in APIServiceKubernetes(service_id).list_cluster_nodes(cluster_id):
            kube_node_ids.append(kube_node["instanceId"])

        for deleted_kube_node in APIServiceKubernetes(service_id).list_cluster_deleted_nodes(cluster_id, False):
            kube_node_ids.append(deleted_kube_node["instanceId"])

    print(f"Kube instance count: {len(kube_node_ids)}")
    if len(kube_node_ids) == 0:
        print("No kube ids, continuing...\n")
        continue

    history_run = ovh_client.get(f"/cloud/project/{service_id}/usage/history")
    if history_run is None:
        exit(0)

    latest_run_id = history_run[0]["id"]
    latest_run_data = ovh_client.get(f"/cloud/project/{service_id}/usage/history/{latest_run_id}")

    if latest_run_data is None:
        exit(0)

    for instance_group in latest_run_data["hourlyUsage"]["instance"]:
        for instance in instance_group["details"]:
            history_instance_ids.append(instance["instanceId"])

    for instance_group in latest_run_data["monthlyUsage"]["instance"]:
        for instance in instance_group["details"]:
            history_instance_ids.append(instance["instanceId"])


    history_matching_ids: list[str] = []
    for history_id in history_instance_ids:
        for kube_id in kube_node_ids:
            if history_id == kube_id:
                history_matching_ids.append(kube_id)


    current_data = ovh_client.get(f"/cloud/project/{service_id}/usage/current")
    if current_data is None:
        exit(0)
        
    for instance_group in current_data["hourlyUsage"]["instance"]:
        for instance in instance_group["details"]:
            current_instance_ids.append(instance["instanceId"])

    for instance_group in current_data["monthlyUsage"]["instance"]:
        for instance in instance_group["details"]:
            current_instance_ids.append(instance["instanceId"])


    display: bool = True
    current_matching_ids: list[str] = []
    for current_id in current_instance_ids:
        for kube_id in kube_node_ids:
            if current_id == kube_id:
                current_matching_ids.append(kube_id)

    print(f"History instance count: {len(history_instance_ids)}")
    print(f"Current instance count: {len(current_instance_ids)}")
    print(f"[History|Kube] matching ids count: {len(history_matching_ids)}")
    print(f"[Current|Kube] matching ids count: {len(current_matching_ids)}")

    print()