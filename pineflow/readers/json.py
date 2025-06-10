import json
import os
from pathlib import Path
from typing import List, Optional

from pineflow.core.document import Document
from pineflow.core.readers import BaseReader


class JSONReader(BaseReader):
    """JSON reader.

    Args:
        jq_schema (str, optional): jq schema to use to extract the data from the JSON.
    """

    jq_schema: Optional[str] = None

    def load_data(self, input_file: str) -> List[Document]:
        """Loads data from the specified file.

        Args:
            input_file (str): File path to load.

        Returns:
            List[Document]: A list of ``Document`` objects loaded from the file.
        """
        try:
            import jq  # noqa: F401
        except ImportError:
            raise ImportError("jq package not found, please install it with `pip install jq`")
        
        if not os.path.isfile(input_file):
            raise ValueError(f"File `{input_file}` does not exist")
        
        documents = []
        jq_compiler = jq.compile(self.jq_schema)
        json_file = Path(input_file).resolve().read_text(encoding="utf-8")
        json_data = jq_compiler.input(json.loads(json_file))
        
        
        for content in json_data:

            if isinstance(content, str):
                content = content
            elif isinstance(content, dict):
                content = json.dumps(content) if content else ""
            else:
                content = str(content) if content is not None else ""
            
            if content.strip() != "":
                documents.append(Document(
                    text=content,
                    metadata={"source": str(Path(input_file).resolve())}))

        return documents
