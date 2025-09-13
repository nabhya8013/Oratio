from fastapi import FastAPI
from pydantic import BaseModel
from speechbrain.pretrained import VAD
import whisper
import numpy as np

app = FastAPI()

class AudioRequest(BaseModel):
    audio_path: str

@app.post("/vad_asr")
async def vad_asr(req: AudioRequest):
    vad = VAD.from_hparams(source="speechbrain/vad-crdnn-libriparty")
    model = whisper.load_model("base")

    prob = vad.get_speech_prob_file(req.audio_path)
    threshold = 0.5
    frames = (prob > threshold).nonzero()[0]
    frame_duration = 30 / len(prob)
    if len(frames) == 0:
        start_time = 0.0
    else:
        start_time = frames[0] * frame_duration

    result = model.transcribe(req.audio_path)
    transcription = result["text"]

    return {"start_time": start_time, "transcription": transcription}
