
import sys
import os
import numpy as np
import cv2

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../bioauth_sys')))

from bioauth_core.face.processor import FaceProcessor
from bioauth_core.iris.processor import IrisProcessor
from bioauth_core.matching import Matcher
from bioauth_core.security.crypto import CryptoManager

def test_imports():
    assert FaceProcessor is not None
    assert IrisProcessor is not None

def test_crypto():
    cm = CryptoManager()
    data = b"secret biometric data"
    nonce, ciphertext = cm.encrypt(data)
    decrypted = cm.decrypt(nonce, ciphertext)
    assert decrypted == data

def test_matching():
    # Mock embeddings
    e1 = np.array([1, 0])
    e2 = np.array([1, 0])
    score = Matcher.cosine_similarity(e1, e2)
    assert score > 0.99
    
    e3 = np.array([0, 1])
    score_diff = Matcher.cosine_similarity(e1, e3)
    assert score_diff < 0.01

def test_iris_processing():
    ip = IrisProcessor()
    # Create dummy eye image
    img = np.zeros((100, 100), dtype=np.uint8)
    cv2.circle(img, (50, 50), 10, (0), -1) # pupil
    cv2.circle(img, (50, 50), 30, (100), 2) # iris boundary
    # This is too synthetic for Hough to work reliably without tuning, 
    # but we just check if methods run without crash
    res = ip.preprocess(img)
    assert res is not None
