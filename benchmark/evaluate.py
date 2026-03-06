
import numpy as np
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
import io

class Benchmarker:
    def __init__(self):
        self.genuine_scores = []
        self.impostor_scores = []

    def add_score(self, score: float, is_genuine: bool):
        if is_genuine:
            self.genuine_scores.append(score)
        else:
            self.impostor_scores.append(score)

    def calculate_metrics(self) -> Dict[str, float]:
        """Calculate EER, FAR, FRR."""
        # Simple EER calculation
        # This is a basic approximation. Production should use simpler threshold sweep.
        
        y_true = [1] * len(self.genuine_scores) + [0] * len(self.impostor_scores)
        y_scores = self.genuine_scores + self.impostor_scores
        
        if not y_true:
            return {}

        fpr, tpr, thresholds = roc_curve(y_true, y_scores)
        fnr = 1 - tpr
        
        # EER is where FPR = FNR
        eer_idx = np.nanargmin(np.absolute((fnr - fpr)))
        eer = fpr[eer_idx]
        
        return {"EER": float(eer), "Optimal_Threshold": float(thresholds[eer_idx])}

    def generate_roc_plot(self) -> bytes:
        """Generate ROC curve image."""
        y_true = [1] * len(self.genuine_scores) + [0] * len(self.impostor_scores)
        y_scores = self.genuine_scores + self.impostor_scores
        
        if not y_true:
            return b""
            
        fpr, tpr, _ = roc_curve(y_true, y_scores)
        
        plt.figure()
        plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic')
        plt.legend(loc="lower right")
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        return buf.getvalue()
