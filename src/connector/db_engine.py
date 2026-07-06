from sqlalchemy import Engine, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

RAW_CONN_URL = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_RAW_NAME')}"
WRHS_CONN_URL = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_WRHS_NAME')}"
FINOPS_MYSQL = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PWD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB_NAME')}"


def get_raw_engine() -> Engine:
    return create_engine(RAW_CONN_URL)

def get_warehouse_engine() -> Engine:
    return create_engine(WRHS_CONN_URL)

def get_finops_mysql_engine() -> Engine:
    return create_engine(FINOPS_MYSQL)