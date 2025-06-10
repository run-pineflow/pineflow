import re
from typing import List, Literal, Tuple

import numpy as np
from pydantic.v1 import BaseModel

from pineflow.core.document import Document
from pineflow.core.embeddings import BaseEmbedding
from pineflow.core.text_chunkers.base import BaseTextChunker
from pineflow.core.utils.pairwise import cosine_similarity


class SemanticChunker(BaseTextChunker, BaseModel):
    """Python class designed to split text into chunks using semantic understanding.

    Credit to Greg Kamradt's notebook:
    `5 Levels Of Text Splitting <https://github.com/FullStackRetrieval-com/RetrievalTutorials/blob/main/tutorials/LevelsOfTextSplitting/5_Levels_Of_Text_Splitting.ipynb>`_.

    Args:
        embed_model (BaseEmbedding): Embedding model used for semantic chunking.
        buffer_size (int, optional): Size of the buffer for semantic chunking. Default is ``1``.
        breakpoint_threshold_amount (int, optional): Threshold percentage for detecting breakpoints. Default is ``95``.
        device (str, optional): Device to use for processing. Currently supports "cpu" and "cuda". Default is ``cpu``.

    Example:
        .. code-block:: python

            from pineflow.core.text_chunkers import SemanticChunker
            from pineflow.embeddings.huggingface import HuggingFaceEmbedding

            embedding = HuggingFaceEmbedding()
            text_chunker = SemanticChunker(embed_model=embedding)
    """

    embed_model: BaseEmbedding
    buffer_size: int = 1
    breakpoint_threshold_amount: int = 95
    device: Literal["cpu", "cuda"] = "cpu"

    class Config:
        arbitrary_types_allowed = True

    def _combine_sentences(self, sentences: List[dict]) -> List[dict]:
        """Combine sentences with neighbors based on buffer size."""
        for i in range(len(sentences)):
            combined_sentence = ""
            
            # Add previous sentences based on buffer size
            for j in range(i - self.buffer_size, i):
                if j >= 0:
                    combined_sentence += sentences[j]["sentence"] + " "

            # Add the current sentence
            combined_sentence += sentences[i]["sentence"]

            # Add next sentences based on buffer size
            for j in range(i + 1, i + 1 + self.buffer_size):
                if j < len(sentences):
                    combined_sentence += " " + sentences[j]["sentence"]

            sentences[i]["combined_sentence"] = combined_sentence
        
        return sentences
        
    def _calculate_cosine_distances(self, single_sentences_list: List[str]) -> Tuple[List[float], List[dict]]:
        _sentences = [{"sentence": x, "index": i} for i, x in enumerate(single_sentences_list)]
        
        sentences = self._combine_sentences(_sentences)
        embeddings = self.embed_model.get_texts_embedding(
            [x["combined_sentence"] for x in sentences]
        )
        
        for i, sentence in enumerate(sentences):
            sentence["combined_sentence_embedding"] = embeddings[i]
            
        distances = []
        for i in range(len(sentences) - 1):
            embedding_current = sentences[i]["combined_sentence_embedding"]
            embedding_next = sentences[i + 1]["combined_sentence_embedding"]
            
            similarity = cosine_similarity(embedding_current, embedding_next)
            
            distance = 1 - similarity
            distances.append(distance)
            
            # Store distance in the dictionary
            sentences[i]["distance_to_next"] = distance
        
        return distances, sentences
    
    def _calculate_breakpoint(self, distances: List[float]) -> List:
        distance_threshold = np.percentile(distances, self.breakpoint_threshold_amount)
        
        return [i for i, x in enumerate(distances) if x > distance_threshold]
        
    def from_text(self, text: str) -> List[str]:
        """Split text into chunks.

        Args:
            text (str): Input text to split.

        Returns:
            List[str]: List of text chunks.
        """
        single_sentences_list = re.split(r"(?<=[.?!])\s+", text)
        distances, sentences = self._calculate_cosine_distances(single_sentences_list)
        
        indices_above_thresh = self._calculate_breakpoint(distances)
        
        chunks = []
        start_index = 0

        for index in indices_above_thresh:
            # Slice the sentence_dicts from the current start index to the end index
            group = sentences[start_index: index + 1]
            combined_text = " ".join([d["sentence"] for d in group])
            chunks.append(combined_text)
            
            # Update the start index for the next group
            start_index = index + 1
            
        # The last group, if any sentences remain
        if start_index < len(sentences):
            combined_text = " ".join([d["sentence"] for d in sentences[start_index:]])
            chunks.append(combined_text)
        
        return chunks
        
    def from_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks.

        Args:
            documents (List[Document]): List of ``Document`` objects to split.

        Returns:
            List[Document]: List of chunked documents objects.
        """
        chunks = []

        for document in documents:
            texts = self.from_text(document.get_content())

            for text in texts:
                chunks.append(Document(
                    text=text, 
                    metadata={ **document.get_metadata(), 
                              "ref_doc_id": document.id_, 
                              "ref_doc_hash": document.hash }))

        return chunks
