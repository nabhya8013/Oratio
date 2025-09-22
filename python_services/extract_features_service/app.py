from fastapi import FastAPI
from pydantic import BaseModel
import parselmouth
import numpy as np

app = FastAPI()

class AudioRequest(BaseModel):
    audio_path: str

@app.post("/extract_features")
async def extract_features(req: AudioRequest):
    sound = parselmouth.Sound(req.audio_path)

    # Pitch extraction
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    pitch_values = pitch_values[pitch_values != 0]  # remove unvoiced frames

    pitch_mean = float(np.mean(pitch_values)) if len(pitch_values) > 0 else 0.0
    pitch_std = float(np.std(pitch_values)) if len(pitch_values) > 0 else 0.0

    # Intensity extraction
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
