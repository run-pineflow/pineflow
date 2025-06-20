from abc import ABC, abstractmethod
from typing import List

from pydantic.v1 import BaseModel

from pineflow.core.document import Document


class BaseReader(ABC, BaseModel):
    """An interface for document reader."""

    @classmethod
    def class_name(cls) -> str:
        return "BaseReader"

    @abstractmethod
    def load_data(self) -> List[Document]:
        """Loads data."""

    def load(self) -> List[Document]:
        return self.load_data()

    def lazy_load(self) -> List[Document]:
        return self.load_data()
