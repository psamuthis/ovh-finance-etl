from dataclasses import dataclass

from etl.dataclass.kube_node import KubeNode


@dataclass
class KubeCluster:
    id: str
    nodes: list[KubeNode]