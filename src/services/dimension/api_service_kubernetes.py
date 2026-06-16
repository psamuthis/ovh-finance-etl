from datetime import datetime, timezone
from typing import Any, Optional

import ovh

from connector.ovh_connection import OVHConnector

ALL_PROJECTS = "/cloud/project"


def SERVICE(service_id: str) -> str:
    return f"{ALL_PROJECTS}/{service_id}"


def CURRENT(service_id: str) -> str:
    return f"{ALL_PROJECTS}/{service_id}/usage/current"


def ALL_CLUSTER(service_id: str) -> str:
    return f"{ALL_PROJECTS}/{service_id}/kube"


def CLUSTER(service_id: str, cluster_id: str) -> str:
    return f"{ALL_PROJECTS}/{service_id}/kube/{cluster_id}"


def ALL_NODE(service_id: str, cluster_id: str) -> str:
    return f"{ALL_PROJECTS}/{service_id}/kube/{cluster_id}/node"

def ALL_DELETED_NODES(service_id: str, cluster_id: str) -> str:
    return f"{ALL_PROJECTS}/{service_id}/kube/{cluster_id}/node?history=True"


def NODE(service_id: str, cluster_id: str, node_id: str) -> str:
    return f"{ALL_PROJECTS}/{service_id}/kube/{cluster_id}/node/{node_id}"


class APIServiceKubernetes:
    ovh_client: ovh.Client = OVHConnector._get_client()

    def __init__(self, service_id: str):
        self.service_id = service_id

    @classmethod
    def list_services(cls) -> list[str]:
        api_response = cls.ovh_client.get(ALL_PROJECTS)
        if not isinstance(api_response, list):
            raise TypeError(f"Expected list in API response: {ALL_PROJECTS}")

        return api_response

    def list_clusters(self) -> list[str]:
        api_response = self.ovh_client.get(ALL_CLUSTER(self.service_id))
        if not isinstance(api_response, list):
            raise TypeError(f"Expected array in API response: {ALL_CLUSTER(self.service_id)}")

        return api_response

    def list_cluster_nodes(self, cluster_id: str) -> list[dict[str, Any]]:
        api_response = self.ovh_client.get(ALL_NODE(self.service_id, cluster_id))
        if not isinstance(api_response, list):
            raise TypeError(
                f"Expected array in API response: {ALL_NODE(self.service_id, cluster_id)}"
            )

        return [node for node in api_response]

    def list_cluster_deleted_nodes(self, cluster_id, active_month: bool = True) -> list[dict[str, Any]]:
        api_response = self.ovh_client.get(ALL_DELETED_NODES(self.service_id, cluster_id))
        if not isinstance(api_response, list):
            raise TypeError(
                f"Expected array in API response: {ALL_DELETED_NODES(self.service_id, cluster_id)}"
            )

        if not active_month:
            return api_response

        filtered_nodes: list[dict[str, Any]] = []
        current_month: datetime = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        for node in api_response:
            if datetime.fromisoformat(node["createdAt"].replace("Z", "+00:00")) < current_month:
                continue

            filtered_nodes.append(node)

        return filtered_nodes

    def get_node_cluster(self, node_id: str) -> Optional[str]:
        cluster_id: str | None = None

        for cluster in self.list_clusters():
            nodes: list[dict[str, Any]] = self.list_cluster_nodes(cluster)

            for node in nodes:
                if node["id"] == node_id:
                    cluster_id = cluster

        return cluster_id

    def get_node_data(self, node_id: str) -> Optional[dict[str, Any]]:
        node_cluster: str | None = self.get_node_cluster(node_id)

        if node_cluster is None:
            return None

        api_response = self.ovh_client.get(NODE(self.service_id, node_cluster, node_id))
        if not isinstance(api_response, dict):
            raise TypeError(
                f"Expected dict in API response: {NODE(self.service_id, node_cluster, node_id)}"
            )

        return api_response

    def get_project_tenant(self) -> str:
        api_response = self.ovh_client.get(SERVICE(self.service_id))
        if not isinstance(api_response, dict):
            raise TypeError(f"Expected dict in API response: {SERVICE(self.service_id)}")

        return api_response["description"]

    def get_project_details(self) -> dict[str, Any]:
        api_response = self.ovh_client.get(SERVICE(self.service_id))
        if not isinstance(api_response, dict):
            raise TypeError(f"Expected dict in API response: {SERVICE(self.service_id)}")

        return api_response

    def find_latest_kube_match(self, instance_ids: list[str]) -> dict[str, dict[str, Any]]: 
        all_nodes: dict[str, dict[str, Any]] = self.all_nodes_in_dict()
        matching_nodes: dict[str, dict[str, Any]] = {}
        
        for instance_id in instance_ids:
            if instance_id in all_nodes:
                matching_nodes[instance_id] = all_nodes[instance_id]

        print(f"input instance count={len(instance_ids)} | match count={len(matching_nodes)}")
        return matching_nodes

    def all_nodes_in_dict(self) -> dict[str, dict[str, Any]]:
        all_nodes: dict[str, dict[str, Any]] = {}
        for cluster in self.list_clusters():
            for node in self.list_cluster_nodes(cluster) + self.list_cluster_deleted_nodes(cluster):
                node["clusterId"] = cluster
                all_nodes[node["instanceId"]] = node

        return all_nodes