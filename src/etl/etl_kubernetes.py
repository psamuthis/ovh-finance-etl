from dataclasses import dataclass
from datetime import datetime

from connector.postgres_connection import WarehouseSessionLocal
from etl.dataclass.kube_cluster import KubeCluster
from etl.dataclass.kube_node import KubeNode
from models.dimension.dim_kubernetes import DimKubernetes
from models.dimension.dim_time import DimTime
from services.db_service import DBService
from services.dimension.api_service_kubernetes import APIServiceKubernetes
from services.dimension.db_service_kubernetes import DBServiceKubernetes
from services.dimension.service_tenant import ServiceTenant
from services.dimension.service_time import ServiceTime


class ETLKubernetes:
    def __init__(self, service_id: str, period_from: datetime, period_to: datetime):
        self.service_id: str = service_id
        self.period_from: datetime = period_from
        self.period_to: datetime = period_to
        self.api_kube: APIServiceKubernetes = APIServiceKubernetes(self.service_id)
        self.kube_data: list[KubeCluster] = []

    def extract_data(self) -> None:
        for cluster in self.api_kube.list_clusters():
            self.kube_data.append(KubeCluster(
                cluster,
                self.extract_nodes(cluster)
            ))

    def extract_nodes(self, cluster_id: str) -> list[KubeNode]:
        cluster_nodes: list[KubeNode] = []
        for node in self.api_kube.list_cluster_nodes(cluster_id):
            cluster_nodes.append(KubeNode(
                node["id"],
                node["projectId"],
                node["instanceId"],
                node["nodePoolId"],
                node["flavor"],
                node["status"],
                node["version"],
                datetime.fromisoformat(node["createdAt"].replace("Z", "+00:00")),
                datetime.fromisoformat(node["updatedAt"].replace("Z", "+00:00")),
                datetime.fromisoformat(node["deployedAt"].replace("Z", "+00:00"))
            )) 

        return cluster_nodes

    def load_data(self) -> None:
        with WarehouseSessionLocal() as db:
            for cluster in self.kube_data:
                for node in cluster.nodes:
                    DBService(db, DimKubernetes).insert_one(DimKubernetes(
                        fk_created_at=ServiceTime(db).get_or_create(node.created_at),
                        fk_updated_at=ServiceTime(db).get_or_create(node.updated_at),
                        fk_deployed_at=ServiceTime(db).get_or_create(node.deployed_at),
                        fk_deleted_at=None,
                        fk_tenant=ServiceTenant(db).get_or_create(self.service_id),
                        cluster_id=cluster.id,
                        nodepool_id=node.nodepool_id,
                        instance_id=node.instance_id,
                        flavor=node.flavor,
                        status=node.status,
                        version=node.version
                    ))

            db.commit()