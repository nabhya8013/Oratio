from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI()

# --- Load Model on Startup ---
# Using a distilled version of RoBERTa fine-tuned on SST-2 for sentiment analysis
# This model is efficient and commonly used. Labels: LABEL_1 -> POSITIVE, LABEL_0 -> NEGATIVE
# Note: This model is primarily positive/negative. We'll treat low scores as neutral.
MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english" 
logging.info(f"Loading sentiment analysis model: {MODEL_NAME}...")
try:
    sentiment_pipeline = pipeline("sentiment-analysis", model=MODEL_NAME)
    logging.info("Sentiment analysis model loaded successfully.")
except Exception as e:
    logging.exception("Failed to load sentiment analysis model on startup.")
    raise e

class SentimentRequest(BaseModel):
    text: str

@app.post("/analyze_sentiment")
async def analyze_sentiment(req: SentimentRequest):
    try:
        logging.info(f"Received request for sentiment analysis on text: '{req.text[:100]}...'") # Log first 100 chars
        
        if not req.text or not req.text.strip():
             logging.warning("Received empty text for sentiment analysis.")
             return {"label": "NEUTRAL", "score": 0.0} # Return neutral for empty input
             
        # Perform sentiment analysis
        result = sentiment_pipeline(req.text)[0] # pipeline returns a list
        
        label = result['label']
        score = result['score']

        # Simplify label (POSITIVE/NEGATIVE) and handle neutrality based on score
        # Note: This model doesn't explicitly output 'NEUTRAL'. We infer it.
        # If the confidence score is low (e.g., < 0.7), we can consider it neutral.
        sentiment_label = "NEUTRAL"
        if score > 0.7: # Confidence threshold
            if label == "POSITIVE":
                sentiment_label = "POSITIVE"
            elif label == "NEGATIVE":
                sentiment_label = "NEGATIVE"
                
        logging.info(f"Analysis complete. Label: {sentiment_label}, Score: {score:.4f} (Original Model Label: {label})")
        
        return {"label": sentiment_label, "score": round(score, 4)}

    except Exception as e:
        logging.exception("Error in analyze_sentiment endpoint.")
        raise HTTPException(status_code=500, detail=str(e))