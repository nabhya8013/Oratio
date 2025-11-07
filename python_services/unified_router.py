# D:\AI PROJECT\Oratio\python_services\unified_router.py
import logging
import uvicorn
import os
import httpx # Import for making internal requests
from fastapi import FastAPI, HTTPException, Body
# Supabase client is imported lazily in non-test mode to avoid requiring the package in TEST_MODE
from dotenv import load_dotenv
load_dotenv()


# Import individual service apps
# --- Test Mode and Service Wiring ---
TEST_MODE = os.environ.get("ORATIO_TEST_MODE", "0") == "1"

# Placeholders so names exist regardless of mode
supabase = None
vad_asr_app = None
features_app = None
ser_app = None
similarity_app = None
prosody_app = None
sentiment_app = None

if TEST_MODE:
    logging.warning("ORATIO_TEST_MODE=1 — Using stub microservices and bypassing Supabase.")

    # Define lightweight stub apps to avoid heavy model downloads
    from fastapi import FastAPI as _FastAPI

    # VAD/ASR stub
    vad_asr_app = _FastAPI()
    @vad_asr_app.post("/vad_asr")
    async def _vad_asr_stub(req: dict):
        return {"start_time": 0.0, "transcription": "this is a test transcription"}

    # Features stub
    features_app = _FastAPI()
    @features_app.post("/extract_features")
    async def _extract_features_stub(req: dict):
        return {"pitch_mean": 120.0, "pitch_std": 5.0, "intensity_mean": 0.7, "intensity_std": 0.1}

    # SER stub
    ser_app = _FastAPI()
    @ser_app.post("/ser")
    async def _ser_stub(req: dict):
        return {"label": "neutral", "score": 0.5}

    # Similarity stub
    similarity_app = _FastAPI()
    @similarity_app.post("/similarity")
    async def _similarity_stub(req: dict):
        t1 = (req or {}).get("text1") or ""
        t2 = (req or {}).get("text2") or ""
        sim = 0.0
        if t1 and t2:
            sim = 0.83 if t1[:5] == t2[:5] else 0.62
        return {"similarity": sim}

    # Prosody stub
    prosody_app = _FastAPI()
    @prosody_app.post("/analyze_prosody")
    async def _prosody_stub(req: dict):
        return {"speech_rate_wpm": 150, "num_pauses": 3, "total_pause_duration_s": 1.2}

    # Sentiment stub
    sentiment_app = _FastAPI()
    @sentiment_app.post("/analyze_sentiment")
    async def _sentiment_stub(req: dict):
        text = (req or {}).get("text") or ""
        label = "POSITIVE" if "good" in text.lower() else "NEUTRAL"
        return {"label": label, "score": 0.9 if label == "POSITIVE" else 0.5}

else:
    # Import individual service apps
    try:
        from vad_asr_service.app import app as vad_asr_app
        from extract_features_service.app import app as features_app
        from analyze_ser_service.app import app as ser_app
        from analyze_similarity_service.app import app as similarity_app
        from analyze_prosody_service.app import app as prosody_app
        from analyze_sentiment_service.app import app as sentiment_app
        logging.info("Successfully imported individual service apps.")
    except ImportError as e:
        logging.exception("Failed to import one or more service apps.")
        raise e

    # --- Supabase Configuration ---
    # LOAD THESE FROM YOUR ENVIRONMENT. DO NOT HARDCODE KEYS.
    # These are the same keys your Go backend uses.
    from supabase import create_client, Client
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")  # service role key

    # Check if keys are loaded
    if not SUPABASE_URL or not SUPABASE_KEY:
        logging.warning("Supabase URL/Key not found. DB-dependent services will fail.")
        supabase = None
    else:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logging.info("Supabase client initialized.")

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Main Application ---
app = FastAPI(title="Oratio Unified Router")

# --- Mount Sub-Applications ---
app.mount("/vad_asr", vad_asr_app)
app.mount("/features", features_app)
app.mount("/ser", ser_app)
app.mount("/similarity", similarity_app)
app.mount("/prosody", prosody_app)
app.mount("/sentiment", sentiment_app)

logging.info("Mounted all sub-applications.")

# --- New Orchestrator Endpoint ---
@app.post("/process_all")
async def process_all_services(
    session_id: int = Body(...),
    audio_base64: str = Body(...),
    original_text: str | None = Body(None)
):
    """
    Orchestrates all 6 speech analysis services.
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase client not initialized. Check env vars.")

    # 1. Fetch original speech text from Supabase
    try:
        resp = supabase.table('sessions').select('speech').eq('id', session_id).execute()
        rows = resp.data or []
        if not rows or not rows[0].get('speech'):
            raise HTTPException(status_code=404, detail=f"Session {session_id} or speech text not found.")
        original_text = rows[0]['speech']
        logging.info(f"Fetched speech text for session {session_id}")
    except Exception as e:
        logging.exception("Failed to fetch from Supabase")
        raise HTTPException(status_code=500, detail=f"Supabase error: {e}")

    # 2. Define the service call chain
    # We will use httpx.AsyncClient to call our own mounted services
    # This assumes all services take {"audio_base64": "..."} and some take text
    
    results = {}
    transcribed_text = None
    
    # We must run this inside an AsyncClient context
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        try:
            # --- VAD & ASR ---
            logging.info("Calling /vad_asr/vad_asr...")
            vad_response = await client.post("/vad_asr/vad_asr", json={"audio_content": audio_base64})
            vad_response.raise_for_status()
            vad_data = vad_response.json()
            results["vad_asr"] = vad_data
            transcribed_text = vad_data.get("transcription") or ""
            if not transcribed_text:
                logging.warning("No transcription returned from /vad_asr")

            logging.info(f"Transcription: {transcribed_text}")

            # --- Similarity ---
            logging.info("Calling /similarity/similarity...")
            sim_response = await client.post("/similarity/similarity", json={
                "text1": original_text,
                "text2": transcribed_text
            })
            sim_response.raise_for_status()
            results["similarity"] = sim_response.json()

            # --- Sentiment (on transcribed text) ---
            logging.info("Calling /sentiment/analyze_sentiment...")
            sent_response = await client.post("/sentiment/analyze_sentiment", json={"text": transcribed_text})
            sent_response.raise_for_status()
            results["sentiment"] = sent_response.json()

            # --- Audio-based services ---
            audio_payload = {"audio_content": audio_base64}

            logging.info("Calling /features/extract_features...")
            feat_response = await client.post("/features/extract_features", json=audio_payload)
            feat_response.raise_for_status()
            results["features"] = feat_response.json()

            logging.info("Calling /ser/ser...")
            ser_response = await client.post("/ser/ser", json=audio_payload)
            ser_response.raise_for_status()
            results["ser"] = ser_response.json()

            logging.info("Calling /prosody/analyze_prosody...")
            pros_response = await client.post("/prosody/analyze_prosody", json={
                "audio_content": audio_base64,
                "transcription": transcribed_text
            })
            pros_response.raise_for_status()
            results["prosody"] = pros_response.json()

        except httpx.HTTPStatusError as e:
            # Handle errors from the internal service calls
            logging.exception(f"Error calling internal service: {e.request.url}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Error in {e.request.url}: {e.response.text}")
        except Exception as e:
            logging.exception("General error during service orchestration")
            raise HTTPException(status_code=500, detail=str(e))

    logging.info("Successfully processed all 6 services.")
    return results

# --- Health Check ---
@app.get("/health", summary="Check if the main router is running")
async def health_check():
    return {"status": "ok", "message": "Main router is operational."}

# --- Run directly ---
if __name__ == "__main__":
    logging.info("Starting Uvicorn server directly...")
    uvicorn.run(
        "unified_router:app",
        host="0.0.0.0",
        port=8000, 
        reload=True
    )