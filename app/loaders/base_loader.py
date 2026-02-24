from abc import ABC, abstractmethod
from typing import List
from app.schemas.common import StructuredBlock


class BaseLoader(ABC):
    @abstractmethod
    def load(self, path: str) -> List[StructuredBlock]:
        raise NotImplementedError