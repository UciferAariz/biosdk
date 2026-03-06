
import requests
import io
from typing import Dict, Union, Optional

class BioAuthClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})

    def health(self) -> Dict:
        """Check system health."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def enroll_face(self, name: str, image_bytes: bytes) -> Dict:
        """Enroll a user's face."""
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        data = {'name': name}
        response = self.session.post(f"{self.base_url}/enroll/face", files=files, data=data)
        response.raise_for_status()
        return response.json()

    def verify_face(self, user_id: int, image_bytes: bytes) -> Dict:
        """Verify a user's face."""
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        data = {'user_id': str(user_id)}
        response = self.session.post(f"{self.base_url}/verify/face", files=files, data=data)
        response.raise_for_status()
        return response.json()

    def identify_face(self, image_bytes: bytes) -> Dict:
        """Identify a user from face."""
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        response = self.session.post(f"{self.base_url}/identify/face", files=files)
        response.raise_for_status()
        return response.json()
