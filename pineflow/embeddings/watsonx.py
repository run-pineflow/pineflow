from typing import Any, List, Optional

from pydantic.v1 import BaseModel, PrivateAttr

from pineflow.core.document import Document
from pineflow.core.embeddings import BaseEmbedding, Embedding


class WatsonxEmbedding(BaseModel, BaseEmbedding):
    """IBM watsonx embedding models.

    Note:
            One of these parameters is required: ``project_id`` or ``space_id``. Not both.

    See https://cloud.ibm.com/apidocs/watsonx-ai#endpoint-url for the watsonx.ai API endpoints.

    Args:
        model_name (str): IBM watsonx.ai model to be used. Defaults to ``ibm/slate-30m-english-rtrvr``.
        api_key (str): watsonx API key.
        url (str): watsonx instance url.
        truncate_input_tokens (str): Maximum number of input tokens accepted. Defaults to ``512``
        project_id (str, optional): watsonx project_id.
        space_id (str, optional): watsonx space_id.

    **Example**

    .. code-block:: python

        from pineflow.embeddings.watsonx import WatsonxEmbedding

        watsonx_embedding = WatsonxEmbedding(api_key="your_api_key",
                                         url="your_instance_url",
                                         project_id="your_project_id")
    """

    model_name: str = "ibm/slate-30m-english-rtrvr"
    api_key: str
    url: str
    truncate_input_tokens: int = 512
    project_id: Optional[str] = None
    space_id: Optional[str] = None

    _client: Any = PrivateAttr()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        try:
            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models import Embeddings as WatsonxEmbeddings

        except ImportError:
            raise ImportError("ibm-watsonx-ai package not found, please install it with `pip install ibm-watsonx-ai`")

        if (not (self.project_id or self.space_id)) or (self.project_id and self.space_id):
            raise ValueError("Must provide one of these parameters [`project_id`, `space_id`], not both.")

        kwargs_params = {
            "model_id": self.model_name,
            "params": {"truncate_input_tokens": self.truncate_input_tokens, "return_options": {"input_text": False}},
            "credentials": Credentials(api_key=self.api_key, url=self.url)
        }

        if self.project_id:
            kwargs_params["project_id"] = self.project_id
        else:
            kwargs_params["space_id"] = self.space_id

        self._client = WatsonxEmbeddings(**kwargs_params)

    def get_text_embedding(self, query: str) -> Embedding:
        """Compute embedding for a single input text.

        Args:
            query (str): Input query string to compute the embedding for.

        Returns:
            List[float]: The embedding vector corresponding to the input query.

        Example:
            .. code-block:: python

                embedded_query = watsonx_embedding.get_text_embedding(
                    "Pineflow is a data framework to load any data in one line of code and connect with AI applications."
                )
        """
        return self.get_texts_embedding([query])[0]

    def get_texts_embedding(self, texts: List[str]) -> List[Embedding]:
        """Compute embeddings for a list of texts.

        Args:
            texts (List[str]): A list of input strings for which to compute embeddings.
        """
        return self._client.embed_documents(texts)

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

