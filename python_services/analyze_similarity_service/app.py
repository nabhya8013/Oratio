# analyze_similarity_service/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util

app = FastAPI()
model = SentenceTransformer('all-MiniLM-L6-v2')

class SimilarityRequest(BaseModel):
    text1: str
    text2: str

@app.post("/similarity")
async def similarity(req: SimilarityRequest):
    embeddings = model.encode([req.text1, req.text2])
    sim = util.cos_sim(embeddings[0], embeddings[1]).item()
    return {"similarity": float(sim)}
