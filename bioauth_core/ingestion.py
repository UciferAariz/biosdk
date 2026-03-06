
import hashlib
import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple, Optional

class Ingestion:
    @staticmethod
    def validate_image(file_bytes: bytes, min_res: Tuple[int, int] = (64, 64)) -> Optional[np.ndarray]:
        """
        Validate and decode image.
        Checks resolution and format.
        """
        # Generate hash
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        
        # Decode
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Invalid image format.")
            
        h, w = img.shape[:2]
        if h < min_res[0] or w < min_res[1]:
            raise ValueError(f"Image resolution too low: {w}x{h}. Minimum required: {min_res[1]}x{min_res[0]}")
            
        return img, file_hash

    @staticmethod
    def calculate_quality(img: np.ndarray) -> float:
        """
        Simple quality score based on Laplacian variance (blur detection).
        Higher is better.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        score = cv2.Laplacian(gray, cv2.CV_64F).var()
        return score
