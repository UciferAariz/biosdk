
import os
import json
from datetime import datetime
from supabase import create_client, Client

class BioAuthDB:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            print("Warning: SUPABASE_URL or SUPABASE_KEY not found in environment.")
        
        self.supabase: Client = create_client(url, key)

    def add_user(self, name: str, embedding: list, status: str = "active") -> str:
        """
        Adds a new user with their face embedding to Supabase.
        Returns the new User UUID.
        """
        data = {
            "name": name,
            "face_embedding": embedding, # vector type handled by supabase-py/postgres
            "status": status,
            "last_verified_at": datetime.utcnow().isoformat()
        }
        response = self.supabase.table("users").insert(data).execute()
        
        # supabase-py v2 returns an object with .data
        if response.data:
            return response.data[0]['id']
        else:
            raise Exception("Failed to insert user into Supabase")

    def search_face(self, vector: list, match_threshold: float = 0.55, match_count: int = 5):
        """
        Searches for similar faces using the 'match_faces' RPC function 
        (which uses pgvector <=> operator).
        """
        params = {
            "query_embedding": vector,
            "match_threshold": match_threshold,
            "match_count": match_count
        }
        response = self.supabase.rpc("match_faces", params).execute()
        
        # Response data structure: [{'id': uuid, 'name': str, 'similarity': float}, ...]
        results = []
        if response.data:
            for item in response.data:
                # API expects list of (id, score) tuples mostly, 
                # but we return full info for flexibility or adapt to previous interface.
                # Previous interface: list of (user_id, score)
                # Note: UUIDs are strings here.
                results.append((item['id'], item['similarity']))
        
        return results

    def get_user(self, user_id: str):
        """Fetch user metadata by ID."""
        response = self.supabase.table("users").select("*").eq("id", user_id).execute()
        if response.data:
            return response.data[0]
        return None
