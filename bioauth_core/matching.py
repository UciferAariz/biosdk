
import numpy as np
from typing import List, Tuple, Dict, Union

class Matcher:
    @staticmethod
    def cosine_similarity(embed1: np.ndarray, embed2: np.ndarray) -> float:
        """Compute cosine similarity."""
        norm1 = np.linalg.norm(embed1)
        norm2 = np.linalg.norm(embed2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(embed1, embed2) / (norm1 * norm2))

    @staticmethod
    def hamming_distance(code1: np.ndarray, code2: np.ndarray) -> float:
        """Compute normalized Hamming distance."""
        if code1.shape != code2.shape:
             # Try to reshape or raise error if fundamentally different
             if code1.size == code2.size:
                 code1 = code1.flatten()
                 code2 = code2.flatten()
             else:
                raise ValueError(f"Shape mismatch: {code1.shape} vs {code2.shape}")
        
        return np.count_nonzero(code1 != code2) / code1.size

    @staticmethod
    def fusion_score(face_score: float, iris_code1: np.ndarray, iris_code2: np.ndarray,
                     w_face: float = 0.6, w_iris: float = 0.4) -> float:
        """
        Multimodal fusion using weighted sum.
        Note: Face score is similarity (higher is better).
        Iris score is distance (lower is better).
        We need to convert Iris distance to similarity: 1 - distance.
        """
        iris_dist = Matcher.hamming_distance(iris_code1, iris_code2)
        iris_sim = 1.0 - iris_dist
        
        final_score = (w_face * face_score) + (w_iris * iris_sim)
        return final_score

    @staticmethod
    def verify(score: float, threshold: float) -> bool:
        return score >= threshold
