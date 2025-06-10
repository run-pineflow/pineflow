import os

# import re
import tempfile
from typing import List

from pineflow.core.document import Document
from pineflow.core.readers import BaseReader
from pineflow.readers import DirectoryReader


class S3Reader(BaseReader):
    """S3 bucket reader.

    Args:
        bucket (str): Name of the S3 bucket.
        ibm_api_key_id (str): IBM Cloud API key.
        ibm_service_instance_id (str): Service instance ID for the IBM COS.
        s3_endpoint_url (str): Endpoint URL for the S3 service.

    Example:
        .. code-block:: python

            from pineflow.readers.s3 import S3Reader

            s3_reader = S3Reader(
                bucket="your_bucket",
                ibm_api_key_id="your_api_key",
                ibm_service_instance_id="your_instance_id",
                s3_endpoint_url="your_api_url"
            )
    """

    def __init__(self, bucket: str,
                 ibm_api_key_id: str = None,
                 ibm_service_instance_id: str = None,
                 s3_endpoint_url: str = None
                 ):

        try:
            import ibm_boto3
            from ibm_botocore.client import Config

            self._ibm_boto3 = ibm_boto3
            self._boto_config = Config
        except ImportError:
            raise ImportError("ibm-cos-sdk package not found, please install it with `pip install ibm-cos-sdk`")

        self.bucket = bucket
        self.ibm_api_key_id = ibm_api_key_id
        self.ibm_service_instance_id = ibm_service_instance_id
        self.s3_endpoint_url = s3_endpoint_url

    def load_data(self) -> List[Document]:
        """Loads data from the specified S3 bucket."""
        ibm_s3 = self._ibm_boto3.resource(
            "s3",
            ibm_api_key_id=self.ibm_api_key_id,
            ibm_service_instance_id=self.ibm_service_instance_id,
            config=self._boto_config(signature_version="oauth"),
            endpoint_url=self.s3_endpoint_url,
        )

        bucket = ibm_s3.Bucket(self.bucket)

        with tempfile.TemporaryDirectory() as temp_dir:
            for obj in bucket.objects.filter(Prefix=""):
                file_path = f"{temp_dir}/{obj.key}"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                ibm_s3.meta.client.download_file(self.bucket, obj.key, file_path)

            # s3_source = re.sub(r"^(https?)://", "", self.s3_endpoint_url)

            return DirectoryReader(input_dir=temp_dir).load_data()
