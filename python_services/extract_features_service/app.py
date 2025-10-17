from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import parselmouth
import numpy as np
import base64
import tempfile
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI()

class AudioContentRequest(BaseModel):
    audio_content: str

@app.post("/extract_features")
async def extract_features(req: AudioContentRequest):
    temp_audio_path = None
    try:
        audio_bytes = base64.b64decode(req.audio_content)

        # --- THE FIX: Create temp file in the current directory ('.') ---
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=".") as temp_audio_file:
            temp_audio_path = temp_audio_file.name
            temp_audio_file.write(audio_bytes)

        logging.info(f"Request audio saved to local temporary file: {temp_audio_path}")

        sound = parselmouth.Sound(temp_audio_path)

        pitch = sound.to_pitch()
        pitch_values = pitch.selected_array['frequency']
        pitch_values = pitch_values[pitch_values != 0]

        pitch_mean = float(np.mean(pitch_values)) if len(pitch_values) > 0 else 0.0
        pitch_std = float(np.std(pitch_values)) if len(pitch_values) > 0 else 0.0

        intensity = sound.to_intensity()
        intensity_values = intensity.values.T.flatten()
        intensity_mean = float(np.mean(intensity_values))
        intensity_std = float(np.std(intensity_values))

        return {
            "pitch_mean": pitch_mean,
            "pitch_std": pitch_std,
            "intensity_mean": intensity_mean,
            "intensity_std": intensity_std
        }
    except Exception as e:
        logging.exception("Error in extract_features endpoint.")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            logging.info(f"Cleaned up local temporary file: {temp_audio_path}")