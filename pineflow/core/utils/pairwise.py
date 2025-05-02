from typing import List

import numpy as np

Matrix = List[float]

def cosine_similarity(X: Matrix, Y: Matrix) -> np.ndarray:
    """Row-wise cosine similarity between two equal-width matrices."""
    X = np.array(X)
    Y = np.array(Y)
    
    if X.shape[0] != Y.shape[0]:
        raise ValueError(
            f"Number of rows in X and Y must be the same. X has shape {X.shape} "
            f"and Y has shape {Y.shape}."
        )
    product = np.dot(X, Y)
    norm = np.linalg.norm(X) * np.linalg.norm(Y)
    
    return product / norm
