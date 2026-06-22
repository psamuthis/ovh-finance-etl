from sqlalchemy import Engine, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

RAW_CONN_URL = f"postgresql+psycopg2://{os.getenv('DB_RAW_USER')}:{os.getenv('DB_RAW_PWD')}@{os.getenv('DB_RAW_HOST')}:{os.getenv('DB_RAW_PORT')}/{os.getenv('DB_RAW_NAME')}"
WRHS_CONN_URL = f"postgresql+psycopg2://{os.getenv('DB_WRHS_USER')}:{os.getenv('DB_wRHS_PWD')}@{os.getenv('DB_WRHS_HOST')}:{os.getenv('DB_WRHS_PORT')}/{os.getenv('DB_WRHS_NAME')}"


def get_raw_engine() -> Engine:
    return create_engine(RAW_CONN_URL)


def get_warehouse_engine() -> Engine:
    return create_engine(WRHS_CONN_URL)
