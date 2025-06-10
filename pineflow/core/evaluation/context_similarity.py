from typing import Dict, List

import numpy as np
from pydantic.v1 import BaseModel

from pineflow.core.embeddings import BaseEmbedding, SimilarityMode


class ContextSimilarityEvaluator(BaseModel):
    """Measures how much context has contributed to the answer’s.
    A higher value suggests a greater proportion of the context is present in the LLM's response.

    Args:
        embed_model (BaseEmbedding): The embedding model used to compute vector representations.
        similarity_mode (str, optional): Similarity strategy to use. Supported options are 
            ``"cosine"``, ``"dot_product"``, and ``"euclidean"``. Defaults to ``"cosine"``.
        similarity_threshold (float, optional): Embedding similarity threshold for determining
            whether a context segment "passes". Defaults to ``0.8``.

    Example:
        .. code-block:: python

            from pineflow.core.evaluation import ContextSimilarityEvaluator
            from pineflow.embeddings.huggingface import HuggingFaceEmbedding

            embedding = HuggingFaceEmbedding()
            ctx_sim_evaluator = ContextSimilarityEvaluator(embed_model=embedding)
    """

    embed_model: BaseEmbedding
    similarity_mode: SimilarityMode = SimilarityMode.COSINE
    similarity_threshold: float = 0.8

    class Config:
        arbitrary_types_allowed = True

    def evaluate(self, contexts: List[str], generated_text: str) -> Dict:
        """
        Args:
            contexts (List[str]): List contexts used to generate LLM response.
            generated_text (str): LLM response based on given context.

        Example:
            .. code-block:: python

                evaluation_result = ctx_sim_evaluator.evaluate(contexts=[], generated_text="<candidate>")
        """
        if not contexts or not generated_text:
            raise ValueError("Must provide these parameters [`contexts`, `generated_text`]")

        evaluation_result = {"contexts_score": [], "score": 0}
        candidate_embedding = self.embed_model.get_text_embedding(generated_text)

        for context in contexts:
            context_embedding = self.embed_model.get_text_embedding(context)
            evaluation_result["contexts_score"].append(
                self.embed_model.similarity(candidate_embedding, context_embedding, mode=self.similarity_mode))

        evaluation_result["score"] = np.mean(evaluation_result["contexts_score"])
        evaluation_result["passing"] = evaluation_result["score"] >= self.similarity_threshold

        return evaluation_result
