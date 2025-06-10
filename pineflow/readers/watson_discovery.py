from datetime import datetime
from logging import getLogger
from typing import List, Optional

from pineflow.core.document import Document
from pineflow.core.readers import BaseReader

logger = getLogger(__name__)


class WatsonDiscoveryReader(BaseReader):
    """Provides functionality to read documents from IBM Watson Discovery.

    For more information, see
    `IBM Watson Discovery Getting Started <https://cloud.ibm.com/docs/discovery-data?topic=discovery-data-getting-started>`_.

    Args:
        url (str): Watson Discovery instance URL.
        api_key (str): Watson Discovery API key.
        project_id (str): Watson Discovery project ID.
        version (str, optional): Watson Discovery API version. Defaults to ``2023-03-31``.
        batch_size (int, optional): Batch size for bulk operations. Defaults to ``50``.
        created_date (str, optional): Load documents created after this date.
            Expected format is ``YYYY-MM-DD``. Defaults to today's date.
        pre_additional_data_field (str, optional): Additional data field to prepend to the Document content.
            Defaults to ``None``.

    Example:
        .. code-block:: python

            from pineflow.readers.watson_discovery import WatsonDiscoveryReader

            discovery_reader = WatsonDiscoveryReader(
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
                 batch_size: int = 50,
                 created_date: str = datetime.today().strftime("%Y-%m-%d"),
                 pre_additional_data_field: str = None
                 ) -> None:
        try:
            from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
            from ibm_watson import DiscoveryV2

        except ImportError:
            raise ImportError("ibm-watson package not found, please install it with `pip install ibm-watson`")

        self.project_id = project_id
        self.batch_size = batch_size
        self.created_date = created_date
        self.pre_additional_data_field = pre_additional_data_field

        try:
            authenticator = IAMAuthenticator(api_key)
            self._client = DiscoveryV2(authenticator=authenticator,
                                       version=version)

            self._client.set_service_url(url)
        except Exception as e:
            logger.error(f"Error connecting to IBM Watson Discovery: {e}")
            raise

    def load_data(self) -> List[Document]:
        """Loads documents from Watson Discovery.

        Example:
            .. code-block:: python

                docs = discovery_reader.load_data()
        """
        from ibm_watson.discovery_v2 import QueryLargePassages
        last_batch_size = self.batch_size
        offset_len = 0
        documents = []
        return_fields = ["extracted_metadata.filename", "extracted_metadata.file_type", "text"]

        if self.pre_additional_data_field:
            return_fields.append(self.pre_additional_data_field)

        while last_batch_size == self.batch_size:
            results = self._client.query(
                project_id=self.project_id,
                count=self.batch_size,
                offset=offset_len,
                return_=return_fields,
                filter="extracted_metadata.publicationdate>={}".format(self.created_date),
                passages=QueryLargePassages(enabled=False)).get_result()

            last_batch_size = len(results["results"])
            offset_len = offset_len + last_batch_size

            # Make sure all retrieved document 'text' exist
            results_documents = [doc for doc in results["results"] if "text" in doc]

            if self.pre_additional_data_field:
                for i, doc in enumerate(results_documents):
                    doc["text"].insert(0, self._get_nested_value(doc, self.pre_additional_data_field))

            documents.extend([Document(id_=doc["document_id"],
                                       text="\n".join(doc["text"]),
                                       metadata={"collection_id": doc["result_metadata"]["collection_id"]} | doc[
                                           "extracted_metadata"])
                              for doc in results_documents])

        return documents

    @staticmethod
    def _get_nested_value(d, key_path, separator: Optional[str] = "."):
        """Accesses a nested value in a dictionary using a string key path."""
        keys = key_path.split(separator)  # Split the key_path using the separator
        nested_value = d

        for key in keys:
            nested_value = nested_value[key]  # Traverse the dictionary by each key

        return nested_value
