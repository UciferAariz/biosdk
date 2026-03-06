
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
import numpy as np
import cv2
import io
import os
from contextlib import asynccontextmanager

from bioauth_core.face.processor import FaceProcessor
from bioauth_core.iris.processor import IrisProcessor
from bioauth_core.db import BioAuthDB
from bioauth_core.ingestion import Ingestion
from bioauth_core.matching import Matcher

# Global instances
face_processor = None
iris_processor = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global face_processor, iris_processor, db
    # Initialize implementation
    # Use CPU context (-1) for broad compatibility
    face_processor = FaceProcessor(model_name='buffalo_l', ctx_id=-1)
    iris_processor = IrisProcessor()
    
    # Ensure storage directory exists (for localized storage if needed)
    os.makedirs("storage", exist_ok=True)

    # Supabase Layout
    # Hardcoded fallback for immediate usage based on User input
    if "SUPABASE_URL" not in os.environ:
        os.environ["SUPABASE_URL"] = "https://mcobfyqmprabozycdwyh.supabase.co"
    if "SUPABASE_KEY" not in os.environ:
        os.environ["SUPABASE_KEY"] = "sb_publishable_kwK6UNL-OGPlswtSY3LnMg_3xZcTkBB"

    try:
        db = BioAuthDB()
    except Exception as e:
        print(f"Failed to connect to Supabase: {e}")
        # Only fallback if absolutely necessary, but here we enforce Supabase
        raise e
    
    print("System intialized.")
    yield
    
    # Cleanup
    if db:
        pass # db close if needed

app = FastAPI(title="BioAuth System", lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Streamlit Cloud, Localhost, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EnrollResponse(BaseModel):
    user_id: str
    modality: str
    status: str

class MatchResponse(BaseModel):
    matched: bool
    score: float
    user_id: Optional[str] = None

@app.post("/enroll/face", response_model=EnrollResponse)
async def enroll_face(name: str = Form(...), file: UploadFile = File(...)):
    content = await file.read()
    try:
        img, _ = Ingestion.validate_image(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Process
    faces = face_processor.process_image(img)
    if len(faces) != 1:
        raise HTTPException(status_code=400, detail=f"Expected 1 face, found {len(faces)}")
    
    embedding = np.array(faces[0]['embedding'])
    
    # DB Operations
    # Supabase expects list (not numpy array) for vector
    try:
        user_id = db.add_user(name, embedding.tolist())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {"user_id": user_id, "modality": "face", "status": "enrolled"}

@app.post("/verify/face", response_model=MatchResponse)
async def verify_face(user_id: str = Form(...), file: UploadFile = File(...)):
    content = await file.read()
    try:
        img, _ = Ingestion.validate_image(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    faces = face_processor.process_image(img)
    if len(faces) == 0:
        raise HTTPException(status_code=400, detail="No face detected")
    
    target_embedding = np.array(faces[0]['embedding'])
    
    # In a real system, we'd fetch the specific user's embedding from DB.
    # Our DB logic supports 'search'. To do 1:1 verify, we need to fetch specifically.
    # Current DB implementation only has 'search'.
    # For now, we search with k=1 and check if returned ID matches.
    # (Note: This is suboptimal for 1:1 but works for MVP logic if we trust the search)
    
    # results = [(id, similarity), ...] from Supabase RPC
    results = db.search_face(target_embedding.tolist(), match_count=5)
    
    matched = False
    score = 0.0
    
    # Check if user_id is in results with high score
    # user_id form param is passed as str (UUID) now, or maybe client sends it as str
    # 'user_id: int = Form(...)' in signature needs change too!
    for uid, s in results:
        if str(uid) == str(user_id):
            score = float(s)
            if Matcher.verify(score, 0.55): 
                matched = True
            break
            
    return {"matched": matched, "score": score, "user_id": str(user_id)}

@app.post("/identify/face", response_model=MatchResponse)
async def identify_face(file: UploadFile = File(...)):
    content = await file.read()
    try:
        img, _ = Ingestion.validate_image(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    faces = face_processor.process_image(img)
    if len(faces) == 0:
        raise HTTPException(status_code=400, detail="No face detected")
        
    target_embedding = np.array(faces[0]['embedding'])
    
    results = db.search_face(target_embedding.tolist(), match_count=1)
    
    if not results:
        return {"matched": False, "score": 0.0}
        
    uid, score = results[0]
    matched = Matcher.verify(float(score), 0.6) 
    
    return {"matched": matched, "score": float(score), "user_id": str(uid) if matched else None}

@app.get("/health")
def health():
    return {"status": "ok"}
