from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from speechbrain.inference.classifiers import EncoderClassifier
import torch
import logging
import base64
import torchaudio
from io import BytesIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI()

logging.info("Loading SER model...")
try:
    classifier = EncoderClassifier.from_hparams(
        source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
        savedir="pretrained_models/emotion-recognition-wav2vec2-IEMOCAP",
        run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
    )
    logging.info("SER model loaded successfully.")
except Exception as e:
    logging.exception("Failed to load SER model on startup.")
    raise e

class AudioContentRequest(BaseModel):
    audio_content: str

@app.post("/ser")
async def analyze_ser(req: AudioContentRequest):
    try:
        logging.info(f"Request received for SER.")
        
        # Load audio from in-memory bytes
        audio_bytes = base64.b64decode(req.audio_content)
        waveform, sample_rate = torchaudio.load(BytesIO(audio_bytes))
        waveform = waveform.to(classifier.device)

        # --- THE DEFINITIVE FIX: Use the correct internal module names from the log ---
        # 1. Pass the waveform through the 'wav2vec2' feature extractor.
        features = classifier.mods.wav2vec2(waveform)
        
        # 2. Pass the features through the 'avg_pool' layer.
        pooled_features = classifier.mods.avg_pool(features)

        # 3. Pass the pooled features through the final 'output_mlp' classification layer.
        prediction = classifier.mods.output_mlp(pooled_features)
        
        logging.info(f"Raw prediction from model: {prediction}")

        # 4. Process the raw output to get the final label and score.
        score, index = torch.max(prediction[0], dim=-1)
        emotion_label = classifier.hparams.label_encoder.decode_torch(index)[0]

        logging.info(f"Success! Label: {emotion_label}, Score: {score.item()}")
        return {"label": emotion_label, "score": score.item()}

    except Exception as e:
        logging.exception("Error in analyze_ser endpoint.")
        raise HTTPException(status_code=500, detail=str(e))