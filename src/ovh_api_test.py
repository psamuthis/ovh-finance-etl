import json
import ovh
from dotenv import load_dotenv

from connector.ovh_connection import OVHConnector

load_dotenv()

ovh_client: ovh.Client = OVHConnector._get_client()
print(f"{ovh_client._endpoint}")
print(f"{ovh_client._application_key}")
print(f"{ovh_client._application_secret}")
print(f"{ovh_client._consumer_key}")

tenants = ovh_client.get("/cloud/project")
print(tenants)
