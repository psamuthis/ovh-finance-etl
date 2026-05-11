import json
import ovh
from dotenv import load_dotenv

from connector.ovh_connection import OVHConnector

load_dotenv()

ovh_client: ovh.Client = OVHConnector._get_client()

tenants = ovh_client.get("/cloud/project")
print(tenants)
