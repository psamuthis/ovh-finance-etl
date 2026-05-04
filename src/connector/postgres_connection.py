from sqlalchemy.orm import sessionmaker

from .db_engine import get_raw_engine, get_warehouse_engine

RawSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_raw_engine())
WarehouseSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=get_warehouse_engine()
)
