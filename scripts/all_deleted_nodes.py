import json

from connector.ovh_connection import OVHConnector
import ovh
from services.dimension.api_service_kubernetes import APIServiceKubernetes


kube_service = APIServiceKubernetes("b41a8077d3ed49c69ddc77ed0b16572e")
cluster_list = kube_service.list_clusters()
deleted_nodes = []

for cluster in cluster_list:
    print(json.dumps(kube_service.list_cluster_deleted_nodes(cluster, False), indent=3))
    exit(0)