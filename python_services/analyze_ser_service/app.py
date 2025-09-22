from fastapi import FastAPI
from pydantic import BaseModel
import torch
from speechbrain.inference import EncoderClassifier
import os

app = FastAPI()

class AudioRequest(BaseModel):
    audio_path: str

# Initialize the model here
model_dir = "D:\\AI PROJECT\\Oratio\\models\\emotion-recognition"
classifier = EncoderClassifier.from_hparams(
    source=model_dir,
    savedir="tmp/emotion-recognition",
    run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
)

@app.post("/ser")
async def analyze_ser(req: AudioRequest):
    audio_path = os.path.abspath(req.audio_path)
    prediction = classifier.classify_file(audio_path)
    return {"label": prediction[0], "score": prediction[1].item()}
