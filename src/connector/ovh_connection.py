from typing import Any, Optional

import ovh
import os
from dotenv import load_dotenv
from sqlalchemy import Enum

load_dotenv()


class OVHConnector:
    _client: Optional[ovh.Client] = None

    @classmethod
    def _get_client(cls) -> ovh.Client:
        if cls._client is None:
            cls._client = ovh.Client(
                endpoint=os.getenv("ENDPOINT"),
                application_key=os.getenv("APPLICATION_KEY"),
                application_secret=os.getenv("APPLICATION_SECRET"),
                consumer_key=os.getenv("CONSUMER_KEY"),
            )

        return cls._client
