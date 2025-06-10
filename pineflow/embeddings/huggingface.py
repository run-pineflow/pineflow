from typing import Any, List, Literal

from pydantic.v1 import BaseModel, PrivateAttr

from pineflow.core.document import Document
from pineflow.core.embeddings import BaseEmbedding, Embedding


class HuggingFaceEmbedding(BaseModel, BaseEmbedding):
    """HuggingFace `sentence_transformers` embedding models.

    Args:
        model_name (str): Hugging Face model to be used. Defaults to ``sentence-transformers/all-MiniLM-L6-v2``.
        device (str, optional): Device to run the model on. Supports ``cpu`` and ``cuda``. Defaults to ``cpu``.

    Example:
        .. code-block:: python

            from pineflow.embeddings.huggingface import HuggingFaceEmbedding

            embedding = HuggingFaceEmbedding()
    """

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: Literal["cpu", "cuda"] = "cpu"

    _client: Any = PrivateAttr()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        from sentence_transformers import SentenceTransformer

        self._client = SentenceTransformer(self.model_name, device=self.device)

    def get_text_embedding(self, query: str) -> Embedding:
        """Compute embedding for a text.

        Args:
            query (str): Input query to compute the embedding.

        Example:
            .. code-block:: python

                embedded_query = embedding.get_text_embedding(
                    "Pineflow is a data framework to load any data in one line of code and connect with AI applications."
                )
        """
        return self.get_texts_embedding([query])[0]

    def get_texts_embedding(self, texts: List[str]) -> List[Embedding]:
        """Compute embeddings for a list of texts.

        Args:
            texts (List[str]): A list of input strings for which to compute embeddings.
        """
        return self._client.encode(texts).tolist()

    def get_documents_embedding(self, documents: List[Document]) -> List[Document]:
        """Compute embeddings for a list of documents.

        Args:
            documents (List[Document]): List of documents to compute embeddings.
        """
        texts = [document.get_content() for document in documents]
        embeddings = self.get_texts_embedding(texts)
        
        for document, embedding in zip(documents, embeddings):
            document.embedding = embedding
        
        return documents
