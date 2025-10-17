from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from speechbrain.inference.VAD import VAD
from speechbrain.inference.ASR import EncoderDecoderASR
import logging
import base64
import torchaudio
import torch
from io import BytesIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI()

logging.info("Loading VAD & ASR models...")
try:
    vad_model = VAD.from_hparams(source="speechbrain/vad-crdnn-libriparty")
    asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-rnnlm-librispeech", savedir="pretrained_models/asr-crdnn-rnnlm-librispeech")
    logging.info("VAD & ASR models loaded successfully.")
except Exception as e:
    logging.exception("Failed to load models on startup.")
    raise e

class AudioContentRequest(BaseModel):
    audio_content: str

@app.post("/vad_asr")
async def vad_asr(req: AudioContentRequest):
    try:
        logging.info(f"Request received for VAD & ASR.")
        
        # --- THE FIX: Load audio from in-memory bytes into a tensor ---
        audio_bytes = base64.b64decode(req.audio_content)
        waveform, sample_rate = torchaudio.load(BytesIO(audio_bytes))

        # Ensure waveform is 2D [batch, samples]
        if waveform.dim() == 1:
            waveform = waveform.unsqueeze(0)
        
        # --- Use the correct tensor-based functions ---
        # 1. Get speech probability tensor
        prob_chunks = vad_model.get_speech_prob_chunk(waveform)
        
        # 2. Get boundaries from the probability tensor
        boundaries = vad_model.get_boundaries(prob_chunks)

        # 3. Transcribe using the waveform tensor
        transcription = asr_model.transcribe_batch(waveform, torch.tensor([1.0]))[0][0]

        start_time = 0.0
        if boundaries.shape[0] > 0:
            start_time = boundaries[0, 0].item()
        
        logging.info(f"Success! Start: {start_time}, Transcription: '{transcription}'")
        return {"start_time": start_time, "transcription": transcription}

    except Exception as e:
        logging.exception("Error in vad_asr endpoint.")
        raise HTTPException(status_code=500, detail=str(e))