# TODO: Deprecated import support for old text chunkers
import warnings

from pineflow.core.text_chunkers.semantic import SemanticChunker
from pineflow.core.text_chunkers.sentence import SentenceChunker
from pineflow.core.text_chunkers.token import TokenTextChunker

warnings.simplefilter("always", DeprecationWarning)
warnings.warn(
            "Deprecated import and will be removed. Use 'pineflow.core.text_chunkers' instead.",
            DeprecationWarning,
            stacklevel=2
        )

__all__ = [
    "SemanticChunker",
    "SentenceChunker",
    "TokenTextChunker",
]
