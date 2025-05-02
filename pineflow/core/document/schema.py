import uuid
from abc import ABC, abstractmethod
from hashlib import sha256
from typing import Any, Dict, List, Optional

from pydantic.v1 import BaseModel, Field, validator


class BaseDocument(ABC, BaseModel):
    """Generic abstract interface for retrievable documents."""

    id_: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique ID of the document.")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="A flat dictionary of metadata fields.")
    embedding: Optional[List[float]] = Field(
        default_factory=None,
        description="Embedding of the document.")

    @validator("metadata", pre=True)
    def _validate_metadata(cls, v) -> Dict:
        if v is None:
            return {}
        return v

    @abstractmethod
    def get_content(self) -> str:
        """Get document content."""

    def get_metadata(self) -> dict:
        """Get metadata."""
        return self.metadata
        
    def get_embedding(self) -> List[float]:
        """Get metadata."""
        return self.embedding
        
    @property
    @abstractmethod
    def hash(self) -> str:
        """Get hash."""
    

class TransformerComponent:
    @abstractmethod
    def __call__(self, documents: List[BaseDocument]) -> List[BaseDocument]:
        """Transform documents."""


class Document(BaseDocument):
    """Generic interface for data document."""

    text: str = Field(default="", description="Text content of the document.")

    @classmethod
    def class_name(cls) -> str:
        return "Document"

    def get_content(self) -> str:
        """Get the text content."""
        return self.text
    
    @property
    def hash(self) -> str:
        """Get document hash."""
        return str(sha256(str(self.text).encode("utf-8", "surrogatepass")).hexdigest())


class DocumentWithScore(BaseModel):
    document: BaseDocument
    score: Optional[float] = None

    @classmethod
    def class_name(cls) -> str:
        return "DocumentWithScore"

    def get_score(self) -> float:
        """Get score."""
        if self.score is None:
            return 0.0
        else:
            return self.score

    # #### pass through methods to BaseDocument ####
    @property
    def id_(self) -> str:
        return self.document.id_

    @property
    def text(self) -> str:
        if isinstance(self.document, Document):
            return self.document.text
        else:
            raise ValueError("Must be a Document to get text.")

    def get_content(self) -> str:
        return self.document.get_content()

    def get_metadata(self) -> str:
        return self.document.get_metadata()
