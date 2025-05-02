from abc import ABC, abstractmethod
from enum import Enum
from typing import List

import numpy as np
from deprecated import deprecated

from pineflow.core.document.schema import Document, TransformerComponent
from pineflow.core.utils.pairwise import cosine_similarity

Embedding = List[float]

class SimilarityMode(str, Enum):
    """Modes for similarity."""
    
    COSINE = "cosine"
    DOT_PRODUCT = "dot_product"
    EUCLIDEAN = "euclidean"


def similarity(embedding1: Embedding, 
               embedding2: Embedding,
               mode: SimilarityMode = SimilarityMode.COSINE):
        """Get embedding similarity."""
        if mode == SimilarityMode.EUCLIDEAN:
            return -float(np.linalg.norm(np.array(embedding1) - np.array(embedding2)))

        elif mode == SimilarityMode.DOT_PRODUCT:
            return np.dot(embedding1, embedding2)

        else:
            return cosine_similarity(embedding1, embedding2)


class BaseEmbedding(TransformerComponent, ABC):
    """An interface for embedding models."""

    @classmethod
    def class_name(cls) -> str:
        return "BaseEmbedding"

    @deprecated(
        version="0.6.8",
        reason="'get_query_embedding' is deprecated and will be removed in next release, use 'get_text_embedding'.",
    )
    def get_query_embedding(self, query: str) -> Embedding:
        """DEPRECATED: use 'get_text_embedding'."""
        return self.get_text_embedding(query)
    
    @abstractmethod
    def get_text_embedding(self, query: str) -> Embedding:
        """Get query embedding."""

    @abstractmethod
    def get_texts_embedding(self, texts: List[str]) -> List[Embedding]:
        """Get text embeddings."""

    @abstractmethod
    def get_documents_embedding(self, documents: List[Document]) -> List[Document]:
        """Get documents embeddings."""

    @staticmethod
    def similarity(embedding1: Embedding, 
                   embedding2: Embedding,
                   mode: SimilarityMode = SimilarityMode.COSINE):
        """Get embedding similarity."""
        return similarity(embedding1, embedding2, mode)

    def __call__(self, documents: List[Document]) -> List[Document]:
        return self.get_documents_embedding(documents)
