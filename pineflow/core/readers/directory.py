import glob
import os
from pathlib import Path
from typing import List, Optional, Type

from pineflow.core.document import Document
from pineflow.core.readers import BaseReader


def _loading_default_supported_readers():
    from pineflow.readers import DocxReader, HTMLReader, PDFReader

    return {
    ".docx": DocxReader,
    ".html": HTMLReader,
    ".pdf": PDFReader,
}


class DirectoryReader(BaseReader):
    """Directory reader.

    Reads files from a directory, optionally filtering by file extension and
    allowing recursive directory traversal.

    Args:
        required_exts (List[str], optional): List of file extensions to filter by.
            Only files with these extensions will be loaded. Defaults to ``None`` (no filtering).
        recursive (bool, optional): Whether to recursively search subdirectories for files.
            Defaults to ``False``.

    """
    
    required_exts: List[str] = [".pdf", ".docx", ".html"]
    recursive: Optional[bool] = False
    file_loader: Optional[dict[str, Type[BaseReader]]] = None

    def load_data(self, input_dir: str) -> List[Document]:
        """Loads data from the specified directory.

        Args:
            input_dir (str): Directory path from which to load the documents.

        Returns:
            List[Document]: A list of documents loaded from the directory.
        """
        if not os.path.isdir(input_dir):
            raise ValueError(f"`{input_dir}` is not a valid directory.")
        
        if self.file_loader is None:
            self.file_loader = _loading_default_supported_readers()
        
        input_dir = Path(input_dir)
        documents = []
        
        pattern_prefix = "**/*" if self.recursive else ""

        for extension in self.required_exts:
            files = glob.glob(os.path.join(input_dir, pattern_prefix + extension), recursive=self.recursive)
            
            for file_dir in files:
                loader_cls = self.file_loader.get(extension)
                if loader_cls:
                    try:
                        #TODO add `file_reader_kwargs`
                        doc = loader_cls().load_data(file_dir)
                        documents.extend(doc)
                    except Exception as e:
                        raise f"Error reading {file_dir}: {e}"
                else:
                    #TODO add `unstructured file` support
                    raise f"Unsupported file type: {extension}"

        return documents
