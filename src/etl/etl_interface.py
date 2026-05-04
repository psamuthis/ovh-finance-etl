from abc import ABC, abstractmethod
from typing import Any


class ETLInterface(ABC):
    @abstractmethod
    def extract_data(self, raw_data: list[dict[str, Any]]) -> None:
        pass

    @abstractmethod
    def load_data(self) -> None:
        pass
