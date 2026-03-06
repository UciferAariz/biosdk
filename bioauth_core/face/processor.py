
import numpy as np
import cv2
import os
from typing import List, Dict, Optional, Tuple

try:
    from insightface.app import FaceAnalysis
    HAS_INSIGHTFACE = True
except ImportError:
    HAS_INSIGHTFACE = False
    print("WARNING: InsightFace not found. Running in DEMO mode with mock face detection.")

class FaceProcessor:
    def __init__(self, model_name: str = 'buffalo_l', ctx_id: int = 0, det_size: Tuple[int, int] = (640, 640)):
        """
        Initialize the Face Processor with InsightFace.
        
        Args:
            model_name (str): Name of the model pack to load.
            ctx_id (int): Context ID (GPU index, -1 for CPU).
            det_size (tuple): Detection size.
        """
        if HAS_INSIGHTFACE:
            self.app = FaceAnalysis(name=model_name)
            self.app.prepare(ctx_id=ctx_id, det_size=det_size)
        else:
            self.app = None
    
    def process_image(self, img: np.ndarray, min_det_score: float = 0.5) -> List[Dict]:
        """
        Detect faces and extract embeddings.
        
        Args:
            img (np.ndarray): BGR image.
            min_det_score (float): Minimum detection confidence to include a face.
            
        Returns:
            List[Dict]: List of face objects with 'bbox', 'kps', 'embedding', 'det_score'.
        """
        if HAS_INSIGHTFACE:
            faces = self.app.get(img)
            results = []
            for face in faces:
                score = float(face.det_score)
                if score < min_det_score:
                    continue  # Skip low-confidence detections
                results.append({
                    'bbox': face.bbox.tolist(),
                    'landmark': face.kps.tolist(),
                    'embedding': face.embedding.tolist(),
                    'det_score': score
                })
            return results
        else:
            # Mock/fallback mode — return empty (no face found) to be fail-safe.
            # InsightFace must be installed for real face detection.
            print("WARNING: InsightFace not installed. No face detection available. Returning empty results.")
            return []

    def compute_similarity(self, embed1: List[float], embed2: List[float]) -> float:
        """
        Compute Cosine Similarity between two embeddings.
        """
        e1 = np.array(embed1)
        e2 = np.array(embed2)
        norm1 = np.linalg.norm(e1)
        norm2 = np.linalg.norm(e2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(e1, e2) / (norm1 * norm2))
