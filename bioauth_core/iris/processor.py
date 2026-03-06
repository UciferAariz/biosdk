
import cv2
import numpy as np
from scipy import signal
from typing import Tuple, Optional, Dict

class IrisProcessor:
    def __init__(self, target_size: Tuple[int, int] = (64, 512)):
        """
        Initialize Iris Processor.
        
        Args:
            target_size (tuple): Size of normalized iris image (height, width).
        """
        self.target_size = target_size

    def preprocess(self, img: np.ndarray) -> np.ndarray:
        """Convert to grayscale if needed."""
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    def segment(self, img: np.ndarray) -> Dict[str, Tuple[int, int, int]]:
        """
        Segment Iris and Pupil using Hough Transform.
        Note: reliable segmentation usually requires U-Net in production.
        This is a heuristic fallback.
        """
        # Pupil detection
        img_blur = cv2.medianBlur(img, 5)
        circles_pupil = cv2.HoughCircles(
            img_blur, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
            param1=100, param2=30, minRadius=10, maxRadius=50
        )
        
        pupil = (0, 0, 0)
        iris = (0, 0, 0)

        if circles_pupil is not None:
             pupil = np.uint16(np.around(circles_pupil[0][0])).tolist()
             pupil = tuple(pupil)
             
             # Iris detection - assume concentric, search larger radius
             # Limit ROI around pupil to speed up
             circles_iris = cv2.HoughCircles(
                img_blur, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                param1=100, param2=30, minRadius=pupil[2] + 20, maxRadius=pupil[2] * 3
             )
             if circles_iris is not None:
                 # Find circle closest to pupil center
                 candidates = circles_iris[0]
                 best_dist = float('inf')
                 for c in candidates:
                     dist = np.sqrt((c[0]-pupil[0])**2 + (c[1]-pupil[1])**2)
                     if dist < best_dist:
                         best_dist = dist
                         iris = tuple(np.uint16(np.around(c)).tolist())
        
        return {'pupil': pupil, 'iris': iris}

    def normalize(self, img: np.ndarray, segmentation: Dict) -> np.ndarray:
        """
        Daugman's Rubber Sheet Model normalization.
        Unwraps the annular ring to a rectangular block.
        """
        pupil = segmentation['pupil'] # (x, y, r)
        iris = segmentation['iris']   # (x, y, r)
        
        if pupil[2] == 0 or iris[2] == 0:
            return np.zeros(self.target_size, dtype=np.uint8)

        # Unwrapping logic
        height, width = self.target_size
        normalized = np.zeros((height, width), dtype=np.uint8)
        
        thetas = np.linspace(0, 2*np.pi, width)
        
        for i in range(width):
            theta = thetas[i]
            # Coordinates on inner boundary
            xp = pupil[0] + pupil[2] * np.cos(theta)
            yp = pupil[1] + pupil[2] * np.sin(theta)
            
            # Coordinates on outer boundary
            xi = iris[0] + iris[2] * np.cos(theta)
            yi = iris[1] + iris[2] * np.sin(theta)
            
            for j in range(height):
                r = j / float(height)
                x = int((1-r)*xp + r*xi)
                y = int((1-r)*yp + r*yi)
                
                # Boundary check
                if 0 <= x < img.shape[1] and 0 <= y < img.shape[0]:
                    normalized[j, i] = img[y, x]
                    
        return normalized

    def extract_features(self, normalized_iris: np.ndarray) -> np.ndarray:
        """
        Extract features using 1D Gabor filter.
        Returns a binary IrisCode (numpy array of 0s and 1s).
        """
        # Create 1D Gabor kernel
        ksize = 31
        sigma = 4.0
        lambd = 10.0
        gamma = 0.5
        psi = 0
        
        kernel = cv2.getGaborKernel((ksize, ksize), sigma, 0, lambd, gamma, psi, ktype=cv2.CV_32F)
        filtered = cv2.filter2D(normalized_iris, cv2.CV_32F, kernel)
        
        # Quantize to binary code
        code = (filtered > 0).astype(np.int8)
        return code.flatten()

    def compute_hamming_distance(self, code1: np.ndarray, code2: np.ndarray) -> float:
        """Compute Hamming Distance between two iris codes."""
        if code1.shape != code2.shape:
            raise ValueError("Iris codes must have same dimension")
            
        mismatch = np.count_nonzero(code1 != code2)
        return mismatch / len(code1)
