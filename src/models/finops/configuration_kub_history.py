from datetime import datetime

from models.base import Base
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class ConfigurationKubHistory(Base):
    __tablename__ = "configuration_kub_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conf_date: Mapped[datetime] = mapped_column(DateTime)
    project_id: Mapped[str] = mapped_column(String(200))
    node_id: Mapped[str] = mapped_column(String(200))
    node_name: Mapped[str] = mapped_column(String(200))
    k8s_version: Mapped[str] = mapped_column(String(200))
    flavor_name: Mapped[str] = mapped_column(String(200))
    nodepool_id: Mapped[str] = mapped_column(String(200))
    instance_id: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[str] = mapped_column(String(200))
    deployed_at: Mapped[str] = mapped_column(String(200))
    deleted_at: Mapped[str] = mapped_column(String(200))