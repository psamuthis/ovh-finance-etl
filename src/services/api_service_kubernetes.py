from typing import Any

import ovh

from connector.ovh_connection import OVHConnector

ALL_PROJECTS = "/cloud/project/"


def SERVICE(service_id: str) -> str:
    return f"{ALL_PROJECTS}{service_id}"


def CURRENT(service_id: str) -> str:
    return f"{ALL_PROJECTS}{service_id}/usage/current"


def ALL_CLUSTER(service_id: str) -> str:
    return f"{ALL_PROJECTS}{service_id}/kube/"


def CLUSTER(service_id: str, cluster_id: str) -> str:
    return f"{ALL_PROJECTS}{service_id}/kube/{cluster_id}"


def ALL_NODE(service_id: str, cluster_id: str) -> str:
    return f"{ALL_PROJECTS}{service_id}/kube/{cluster_id}/node"


def NODE(service_id: str, cluster_id: str, node_id: str) -> str:
    return f"{ALL_PROJECTS}{service_id}/kube/{cluster_id}/node/{node_id}"


class APIServiceKubernetes:
    ovh_client: ovh.Client = OVHConnector._get_client()

    def __init__(self, service_id: str):
        self.service_id = service_id

    def list_clusters(self) -> list[str]:
        api_response = self.ovh_client.get(ALL_CLUSTER(self.service_id))
        if not isinstance(api_response, list):
            raise TypeError(
                f"Expected array in API response: {ALL_CLUSTER(self.service_id)}"
            )

        return api_response

    def list_cluster_nodes(self, cluster_id: str) -> list[dict[str, Any]]:
        api_response = self.ovh_client.get(ALL_NODE(self.service_id, cluster_id))
        if not isinstance(api_response, list):
            raise TypeError(
                f"Expected array in API response: {ALL_NODE(self.service_id, cluster_id)}"
            )

        return [node for node in api_response]

    def get_node_cluster(self, node_id: str) -> str:
        cluster_id: str | None = None

        for cluster in self.list_clusters():
            nodes: list[dict[str, Any]] = self.list_cluster_nodes(cluster)

            for node in nodes:
                if node["id"] == node_id:
                    cluster_id = cluster

        if cluster_id is None:
            raise ValueError(f"Node {node_id} was not found in any clusters...")

        return cluster_id

    def get_node_data(self, node_id: str) -> dict[str, Any]:
        api_response = self.ovh_client.get(
            NODE(self.service_id, self.get_node_cluster(node_id), node_id)
        )
        if not isinstance(api_response, dict):
            raise TypeError(
                f"Expected dict in API response: {NODE(self.service_id, self.get_node_cluster(node_id), node_id)}"
            )

        return api_response

    def get_tenant(self) -> str:
        api_response = self.ovh_client.get(SERVICE(self.service_id))
        if not isinstance(api_response, dict):
            raise TypeError(
                f"Expected dict in API response: {SERVICE(self.service_id)}"
            )

        return api_response["description"]
