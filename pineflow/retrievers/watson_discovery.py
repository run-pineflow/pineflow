from logging import getLogger
from typing import List

from deprecated import deprecated

from pineflow.core.document import Document, DocumentWithScore

logger = getLogger(__name__)


class WatsonDiscoveryRetriever:
    """Provides functionality to interact with IBM Watson Discovery for querying documents.

    For more information, see
    `IBM Watson Discovery Getting Started <https://cloud.ibm.com/docs/discovery-data?topic=discovery-data-getting-started>`_.

    Args:
        url (str): Watson Discovery instance URL.
        api_key (str): Watson Discovery API key.
        project_id (str): Watson Discovery project ID.
        version (str, optional): Watson Discovery API version. Defaults to ``2023-03-31``.
        disable_passages (bool, optional): Return the full document instead of passages.
            Only enable this if all documents are short. Defaults to ``False``.

    Example:
        .. code-block:: python

            from pineflow.retrievers.watson_discovery import WatsonDiscoveryRetriever

            doc_retriever = WatsonDiscoveryRetriever(
                url="your_url",
                api_key="your_api_key",
                project_id="your_project_id"
            )
    """

    def __init__(self,
                 url: str,
                 api_key: str,
                 project_id: str,
                 version: str = "2023-03-31",
                 disable_passages: bool = False
                 ) -> None:
        try:
            from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
            from ibm_watson import DiscoveryV2

        except ImportError:
            raise ImportError("ibm-watson package not found, please install it with `pip install ibm-watson`")

        self.disable_passages = disable_passages
        self.project_id = project_id

        try:
            authenticator = IAMAuthenticator(api_key)
            self._client = DiscoveryV2(authenticator=authenticator,
                                       version=version)

            self._client.set_service_url(url)
        except Exception as e:
            logger.error(f"Error connecting to IBM Watson Discovery: {e}")
            raise
    
    @deprecated(
        version="0.6.8",
        reason="'query' is deprecated and will be removed in next release, use 'search_documents'.",
    )
    def query(self, query: str, filter: str = None, top_k: int = 4) -> List[DocumentWithScore]:
        """DEPRECATED: use 'search_documents'."""
        return self.search_documents(query,
                                     filter,
                                     top_k)
        
    def search_documents(self, query: str, filter: str = None, top_k: int = 4) -> List[DocumentWithScore]:
        """Search your data in the Discovery API and return a list of documents.

        Args:
            query (str): Query text.
            filter (str, optional): Searches for documents that match the filter.
                Use Discovery Query Language syntax. Defaults to ``None``.
            top_k (int, optional): Number of top results to return. Defaults to ``4``.

        Example:
            .. code-block:: python

                docs = doc_retriever.query("What's Pineflow?")
        """
        from ibm_watson.discovery_v2 import QueryLargePassages
        return_fields = ["extracted_metadata.filename", "extracted_metadata.file_type"]

        if not self.disable_passages:
            return_fields.append("passages")
        else:
            return_fields.append("text")

        discovery_results = self._client.query(
            project_id=self.project_id,
            natural_language_query=query,
            count=top_k,
            return_=return_fields,
            filter=filter,
            passages=QueryLargePassages(enabled=not self.disable_passages,
                                        per_document=False,
                                        count=top_k,
                                        find_answers=False,
                                        characters=600)
        ).get_result()

        docs_and_scores = []

        if not self.disable_passages and len(discovery_results["passages"]) > 0:
            # If not `disable_passages`, always use discovery passages (recommended)
            for passage in discovery_results["passages"]:
                document_id_target = passage["document_id"]
                document = [doc for doc in discovery_results["results"] if doc["document_id"] == document_id_target]

                docs_and_scores.append(DocumentWithScore(
                    document=Document(
                        text=passage["passage_text"],
                        metadata={"collection_id": passage["collection_id"]} | document[0]["extracted_metadata"]),
                    score=passage["passage_score"] / 100))

        elif discovery_results["matching_results"] > 0:
            # If `disable_passages`, use document text (not recommended,
            # make sure that all documents are short to not exceed the model context window)
            logger.warning("Not recommended to disable passages. Make sure that all documents are short to not "
                            "exceed the model context window.")
            for document in discovery_results["results"]:
                docs_and_scores.append(DocumentWithScore(
                    document=Document(
                        text=" ".join(document["text"]),
                        metadata={"collection_id": document["result_metadata"]["collection_id"]} | document[
                            "extracted_metadata"]),
                    score=document["result_metadata"]["confidence"]))

        return docs_and_scores
