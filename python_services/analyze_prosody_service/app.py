from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import parselmouth
import logging
import base64
import tempfile
import os
from io import BytesIO
import torchaudio
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
app = FastAPI()


class ProsodyRequest(BaseModel):
    audio_content: str
    transcription: str


@app.post("/analyze_prosody")
async def analyze_prosody(req: ProsodyRequest):
    temp_audio_path = None
    try:
        logging.info("Received request for prosody analysis.")
        audio_bytes = base64.b64decode(req.audio_content)

        # --- Load audio & compute duration ---
        waveform, sample_rate = torchaudio.load(BytesIO(audio_bytes))
        duration_seconds = float(waveform.shape[-1]) / float(sample_rate)
        logging.info(f"Audio duration: {duration_seconds:.2f} seconds")

        # --- Write to temporary file ---
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=".") as temp_audio_file:
            temp_audio_path = temp_audio_file.name
            temp_audio_file.write(audio_bytes)
        logging.info(f"Temporary audio saved at {temp_audio_path}")

        # --- Load into Parselmouth ---
        sound = parselmouth.Sound(temp_audio_path)

        # --- Compute Speech Rate ---
        word_count = len(req.transcription.split())
        speech_rate_wpm = int(round((word_count / duration_seconds) * 60)) if duration_seconds > 0 else 0
        logging.info(f"Word count: {word_count}, Speech rate: {speech_rate_wpm} WPM")

        # --- Parameters for silence detection ---
        pitch_floor = 75.0  # Minimum pitch in Hz (must be > 0)
        time_step = 0.0     # Automatic
        silence_threshold_db = -25.0
        min_silence_duration_s = 0.3
        min_sounding_duration_s = 0.1
        silent_label = "silent"
        sounding_label = "sounding"

        logging.info("Running Praat command: To TextGrid (silences)...")

        # --- Main Praat call (correct parameter order) ---
        textgrid = parselmouth.praat.call(
            sound,
            "To TextGrid (silences)",
            float(pitch_floor),
            float(time_step),
            float(silence_threshold_db),
            float(min_silence_duration_s),
            float(min_sounding_duration_s),
            silent_label,
            sounding_label,
        )

        # --- Analyze Intervals ---
        num_intervals = int(parselmouth.praat.call(textgrid, "Get number of intervals", 1))
        logging.info(f"TextGrid created with {num_intervals} intervals.")

        actual_pauses = 0
        total_pause_duration = 0.0

        for i in range(1, num_intervals + 1):
            label = parselmouth.praat.call(textgrid, "Get label of interval", 1, i)
            if label == silent_label:
                start_time = float(parselmouth.praat.call(textgrid, "Get start time of interval", 1, i))
                end_time = float(parselmouth.praat.call(textgrid, "Get end time of interval", 1, i))
                total_pause_duration += (end_time - start_time)
                actual_pauses += 1

        logging.info(f"Detected pauses: {actual_pauses}, total pause duration: {total_pause_duration:.2f} seconds")

        return {
            "speech_rate_wpm": speech_rate_wpm,
            "num_pauses": actual_pauses,
            "total_pause_duration_s": round(total_pause_duration, 2),
        }

    except Exception as e:
        logging.exception("Error in analyze_prosody endpoint.")
        if isinstance(e, parselmouth.PraatError):
            raise HTTPException(
                status_code=500,
                detail=f"Praat command failed. Ensure Praat is correctly installed and accessible. Original error: {e}",
            )
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            logging.info(f"Cleaned up temporary file: {temp_audio_path}")
