from abc import ABC, abstractmethod
from typing import List

from pineflow.core.document.schema import Document, TransformerComponent


class BaseTextChunker(TransformerComponent, ABC):
    """An interface for text chunker."""

    @classmethod
    def class_name(cls) -> str:
        return "BaseTextChunker"

    @abstractmethod
    def from_text(self, text: str) -> List[str]:
        """Chunk text."""

    @abstractmethod
    def from_documents(self, documents: List[Document]) -> List[Document]:
        """Chunk list of documents."""

    def __call__(self, documents: List[Document]) -> List[Document]:
        return self.from_documents(documents)