
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
from typing import Tuple

class CryptoManager:
    def __init__(self, key: bytes = None):
        """
        Initialize with a 32-byte key for AES-256.
        If no key provided, generates one (in-memory only).
        """
        self.key = key if key else os.urandom(32)
        
    def encrypt(self, data: bytes) -> Tuple[bytes, bytes]:
        """
        Encrypt data using AES-GCM.
        Returns (nonce, ciphertext).
        """
        nonce = os.urandom(12)
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(nonce),
            backend=default_backend()
        ).encryptor()
        
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return nonce, ciphertext + encryptor.tag

    def decrypt(self, nonce: bytes, data: bytes) -> bytes:
        """
        Decrypt data using AES-GCM.
        Expects data to be ciphertext + tag.
        """
        tag = data[-16:]
        ciphertext = data[:-16]
        
        decryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        ).decryptor()
        
        return decryptor.update(ciphertext) + decryptor.finalize()

    def get_key_hex(self) -> str:
        return self.key.hex()
