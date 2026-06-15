from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Uuid


@dataclass
class KubeNode:
    id: Uuid
    project_id: str
    instance_id: Uuid
    nodepool_id: Uuid
    flavor: str
    status: str
    version: str
    created_at: datetime
    updated_at: datetime
    deployed_at: datetime