import uuid
from logging import getLogger
from typing import Dict, List, Literal

from pineflow.core.document import Document, DocumentWithScore
from pineflow.core.embeddings import BaseEmbedding
from pineflow.core.vector_stores.base import BaseVectorStore

logger = getLogger(__name__)


class ElasticsearchVectorStore(BaseVectorStore):
    """Provides functionality to interact with Elasticsearch for storing and querying document embeddings.

    Args:
        index_name (str): Name of the Elasticsearch index.
        url (str): Elasticsearch instance URL.
        embed_model (BaseEmbedding): Embedding model used to compute vectors.
        user (str, optional): Elasticsearch username.
        password (str, optional): Elasticsearch password.
        batch_size (int, optional): Batch size for bulk operations. Defaults to ``200``.
        ssl (bool, optional): Whether to use SSL. Defaults to ``False``.
        distance_strategy (str, optional): Distance strategy for similarity search.
            Currently supports ``"cosine"``, ``"dot_product"``, and ``"l2_norm"``. Defaults to ``cosine``.
        text_field (str, optional): Name of the field containing text. Defaults to ``text``.
        vector_field (str, optional): Name of the field containing vector embeddings. Defaults to ``embedding``.

    Example:
        .. code-block:: python

            from pineflow.embeddings.huggingface import HuggingFaceEmbedding
            from pineflow.vector_stores.elasticsearch import ElasticsearchVectorStore

            embedding = HuggingFaceEmbedding()
            es_vector_store = ElasticsearchVectorStore(
                index_name="pineflow-index",
                url="http://localhost:9200",
                embed_model=embedding
            )
    """

    def __init__(self,
                 index_name: str,
                 url: str,
                 embed_model: BaseEmbedding,
                 user: str = "",
                 password: str = "",
                 batch_size: int = 200,
                 ssl: bool = False,
                 distance_strategy: Literal["cosine", "dot_product", "l2_norm"] = "cosine",
                 text_field: str = "text",
                 vector_field: str = "embedding",
                 ) -> None:
        try:
            from elasticsearch import Elasticsearch
            from elasticsearch.helpers import bulk

            self._es_bulk = bulk
        except ImportError:
            raise ImportError("elasticsearch package not found, please install it with `pip install elasticsearch`")

        #  TO-DO: Add connections types e.g: cloud
        self._embed_model = embed_model
        self.index_name = index_name
        self.batch_size = batch_size
        self.distance_strategy = distance_strategy
        self.vector_field = vector_field
        self.text_field = text_field

        self._client = Elasticsearch(
            hosts=[url],
            basic_auth=(
                user,
                password
            ),
            verify_certs=ssl,
            ssl_show_warn=False
        )

        try:
            self._client.info()
        except Exception as e:
            logger.error(f"Error connecting to Elasticsearch: {e}")
            raise

    def _create_index_if_not_exists(self) -> None:
        """Creates the Elasticsearch index if it doesn't already exist."""
        if self._client.indices.exists(index=self.index_name):
            logger.info(f"Index {self.index_name} already exists. Skipping creation.")

        else:
            # Get embedding dims dynamically
            dims_length = len(self._embed_model.get_text_embedding("Elasticsearch"))

            index_mappings = {
                "dynamic_templates": 
                    [{
                    "dynamic_metadata": {
                        "path_match": "metadata.*",
                        "mapping": {
                            "type": "keyword"
                            }
                        }
                    }],
                "properties": {
                    self.text_field: {"type": "text"},
                    self.vector_field: {
                        "type": "dense_vector",
                        "dims": dims_length,
                        "index": True,
                        "similarity": self.distance_strategy,
                    },
                }
            }

            print(f"Creating index {self.index_name}")

            self._client.indices.create(index=self.index_name, mappings=index_mappings)

    def _dynamic_metadata_mapping(self, metadata) -> dict:
        """Dynamic maps metadata object into keyword fields."""
        metadata_mapping = {}
        for key, value in metadata.items():
            metadata_mapping[f"metadata.{key}"] = value
        return metadata_mapping
    
    def add_documents(self, documents: List[Document], create_index_if_not_exists: bool = True) -> List[str]:
        """Add documents to the Elasticsearch index.

        Args:
            documents (List[Document]): List of documents to add to the index.
            create_index_if_not_exists (bool, optional): Whether to create the index if it doesn't exist. Defaults to ``True``.
        """
        if create_index_if_not_exists:
            self._create_index_if_not_exists()

        vector_store_data = []
        for doc in documents:
            _id = doc.id_ if doc.id_ else str(uuid.uuid4())
            _metadata = {**doc.get_metadata(), "hash": doc.hash}
            _metadata_mapping = self._dynamic_metadata_mapping(_metadata)
            vector_store_data.append({
                "_index": self.index_name,
                "_id": _id,
                self.text_field: doc.get_content(),
                self.vector_field: doc.embedding if doc.embedding else self._embed_model.get_text_embedding(doc.get_content()),
                "metadata": _metadata,
                **_metadata_mapping
            })

        self._es_bulk(self._client, vector_store_data, chunk_size=self.batch_size, refresh=True)
        print(f"Added {len(vector_store_data)} documents to `{self.index_name}`")
        
        return [doc.id_ for doc in documents]

    def search_documents(self, query: str, top_k: int = 4) -> List[DocumentWithScore]:
        """Performs a similarity search for the top-k most similar documents.

        Args:
            query (str): Query text.
            top_k (int, optional): Number of top results to return. Defaults to ``4``.

        Returns:
            List[DocumentWithScore]: List of the most similar documents.
        """
        query_embedding = self._embed_model.get_text_embedding(query)
        #  TO-DO: Add elasticsearch `filter` option
        es_query = {"knn": {
            # "filter": filter,
            "field": self.vector_field,
            "query_vector": query_embedding,
            "k": top_k,
            "num_candidates": top_k * 10,
        }}
        
        from elasticsearch import NotFoundError
        
        try:    
            data = self._client.search(
                index=self.index_name,
                **es_query,
                size=top_k,
                _source={"excludes": [self.vector_field]})
        except NotFoundError as e:
            if e.status_code == 404 and e.error == "index_not_found_exception":
                return []
            else:
                raise e

        hits = data.get("hits", {}).get("hits", [])

        return [DocumentWithScore(
            document=Document(
                id_=hit["_id"],
                text=hit["_source"]["text"],
                metadata=hit["_source"]["metadata"],
            ),
            score=hit["_score"])
            for hit in hits
        ]

    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents from the Elasticsearch index.

        Args:
            ids (List[str]): List of documents IDs to delete.
        """
        for id in ids:
            self._client.delete(index=self.index_name, id=id)

    def get_all_documents(self, include_fields: List[str] = []) -> List[Dict[str, Dict]]:
        """Get all documents from vector store."""
        es_query = { "query": { "match_all": {} } }
        
        if len(include_fields):
            es_query["_source"] = include_fields
            
        from elasticsearch import NotFoundError
        
        try:    
            data = self._client.search(
                index=self.index_name, 
                scroll="2m",
                size=1000,
                body=es_query,
                )
        except NotFoundError as e:
            if e.status_code == 404 and e.error == "index_not_found_exception":
                return []
            else:
                raise e
            
        scroll_id = data["_scroll_id"]
        hits = data.get("hits", {}).get("hits", [])
        
        documents = [{ "_source": { "_id": hit["_id"], **hit["_source"] }} for hit in hits]
        

        while len(hits) > 0:
            scroll_data = self._client.scroll(scroll_id=scroll_id, scroll="2m")
            scroll_id = scroll_data["_scroll_id"]
            
            hits = scroll_data.get("hits", {}).get("hits", [])
            
            documents.extend([{ "_source": { "_id": hit["_id"], **hit["_source"] }} for hit in hits])
            
        return documents
