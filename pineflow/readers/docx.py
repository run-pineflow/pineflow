import os
from pathlib import Path
from typing import List

from pineflow.core.document import Document
from pineflow.core.readers import BaseReader


class DocxReader(BaseReader):
    """Microsoft Word (Docx) reader."""

    def load_data(self, input_file: str) -> List[Document]:
        """Loads data from the specified file.

        Args:
            input_file (str): File path to load.

        Returns:
            List[Document]: A list of ``Document`` objects loaded from the file.
        """
        try:
            import docx2txt  # noqa: F401
        except ImportError:
            raise ImportError("docx2txt package not found, please install it with `pip install docx2txt`")
        
        if not os.path.isfile(input_file):
            raise ValueError(f"File `{input_file}` does not exist")
        
        input_file = str(Path(input_file).resolve())

        text = docx2txt.process(input_file)
        metadata = {"source": input_file}

        return [Document(text=text, metadata=metadata)]
