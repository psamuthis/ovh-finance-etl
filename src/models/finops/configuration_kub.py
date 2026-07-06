from datetime import datetime

from models.base import Base
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class ConfigurationKub(Base):
    __tablename__ = "configuration_kub"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conf_date: Mapped[datetime] = mapped_column(DateTime)
    project_id: Mapped[str] = mapped_column(String(200))
    conf_id: Mapped[str] = mapped_column(String(200))
    cluster_name: Mapped[str] = mapped_column(String(200))
    k8s_version: Mapped[str] = mapped_column(String(200))
    flavor_name: Mapped[str] = mapped_column(String(200))
    nodepool_id: Mapped[str] = mapped_column(String(200))
    instance_id: Mapped[str] = mapped_column(String(200))
    savings_plan_id: Mapped[str] = mapped_column(String(200))