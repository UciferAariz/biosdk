Due to Funding Issues this project has been abandoned.
If you have funds then mail us at aarizasdaque@gmail.com , we will retry building it. 

Fund Required - - 2500$



# BioAuth System

## Overview
BioAuth is an end-to-end Face and Iris Biometric Authentication System. It includes:
- **Core Biometric Engine**: Face (InsightFace/ArcFace) and Iris (Daugman/Gabor) recognition.
- **Secure Storage**: AES-256 encrypted biometric templates.
- **REST API**: FastAPI-based endpoints for enrollment, verification, and identification.
- **SDK**: Python client for easy integration.
- **Benchmarking**: Tools to calculate FAR/FRR/EER and generate ROC curves.
- **Dashboard**: Streamlit admin interface.

## Installation

1.  **Clone the repository**.
    ```bash
    git clone <url>
    cd bioauth_sys
    ```

2.  **Install Dependencies**.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the API Server**.
    ```bash
    cd api
    uvicorn main:app --reload
    ```
    API will be available at `http://localhost:8000`.

4.  **Run the Dashboard**.
    ```bash
    streamlit run dashboard/app.py
    ```

## Usage

### Enrollment
Use the Dashboard or API to enroll a user with a face image.
```python
client.enroll_face("John Doe", image_bytes)
```

### Verification
Verify a user ID against a live image.
```python
client.verify_face(user_id, image_bytes)
```

## Structure
- `bioauth_core/`: Core logic (Face, Iris, Security, DB).
- `api/`: REST API.
- `sdk/`: Python wrapper.
- `dashboard/`: UI.
- `benchmark/`: Evaluation tools.

## Security
Templates are encrypted using AES-256-GCM before storage.
Raw images are NOT stored by default.
