# D:\AI PROJECT\Oratio\python_services\unified_router.py
import logging
from fastapi import FastAPI
import uvicorn # Import uvicorn for running if __name__ == "__main__"

# Import the 'app' object from each individual service's app.py
# The paths are relative to this file's location (python_services directory)
try:
    from vad_asr_service.app import app as vad_asr_app
    from extract_features_service.app import app as features_app
    from analyze_ser_service.app import app as ser_app
    from analyze_similarity_service.app import app as similarity_app
    from analyze_prosody_service.app import app as prosody_app
    from analyze_sentiment_service.app import app as sentiment_app
    logging.info("Successfully imported individual service apps.")
except ImportError as e:
    logging.exception("Failed to import one or more service apps. Ensure each service directory has a valid app.py containing 'app = FastAPI()'.")
    raise e

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Main Application ---
# This app acts as the entry point and router
app = FastAPI(title="Oratio Unified Router")

# --- Mount Sub-Applications ---
# Mount each individual service under a specific path prefix
app.mount("/vad_asr", vad_asr_app)
app.mount("/features", features_app)
app.mount("/ser", ser_app)
app.mount("/similarity", similarity_app)
app.mount("/prosody", prosody_app)
app.mount("/sentiment", sentiment_app)

logging.info("Mounted all sub-applications.")

# --- Health Check for the Router ---
@app.get("/health", summary="Check if the main router is running")
async def health_check():
    # You could add checks here later to ping the sub-apps if needed
    return {"status": "ok", "message": "Main router is operational."}

# --- Optional: Run directly with uvicorn ---
# This allows running `python unified_router.py`
if __name__ == "__main__":
    logging.info("Starting Uvicorn server directly...")
    uvicorn.run(
        "unified_router:app", # Point to this file and the app object
        host="0.0.0.0",
        port=8000, # Main router runs on port 8000
        reload=True # Enable reload for development
    )