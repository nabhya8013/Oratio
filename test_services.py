import requests
import os
import base64

# --- CONFIGURATION ---
TEST_AUDIO_FILE = "D:\\AI PROJECT\\Oratio\\clips\\q1_16k.wav" 
REFERENCE_SCRIPT = "ALL RIGHT ALL RIGHT SETTLE DOWN KIDS"

# --- SERVICE URLS ---
VAD_ASR_URL = "http://localhost:8000/vad_asr"
EXTRACT_FEATURES_URL = "http://localhost:8001/extract_features"
ANALYZE_SER_URL = "http://localhost:8002/ser"
SIMILARITY_URL = "http://localhost:8003/similarity"
PROSODY_URL = "http://localhost:8004/analyze_prosody"
SENTIMENT_URL = "http://localhost:8005/analyze_sentiment"


def test_service(service_name, url, json_payload):
    """A generic function to test a service endpoint."""
    print(f"---  TESTING: {service_name} ---")
    try:
        response = requests.post(url, json=json_payload)
        if response.status_code == 200:
            print("✅ Success!")
            print("Response:", response.json())
            return response.json()
        else:
            print(f"❌ Error: Received status code {response.status_code}")
            print("Response:", response.text)
            return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Could not connect to {service_name} at {url}")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return None
    finally:
        print("-" * 30 + "\n")

if __name__ == "__main__":
    print("🚀 Starting Oratio services test...\n")

    if not os.path.exists(TEST_AUDIO_FILE):
        print(f"❌ CRITICAL ERROR: Test audio file not found at '{TEST_AUDIO_FILE}'")
    else:
        # --- Read file and encode to base64 ---
        with open(TEST_AUDIO_FILE, "rb") as f:
            audio_bytes = f.read()
            audio_b64_content = base64.b64encode(audio_bytes).decode('utf-8')
        
        audio_payload = {"audio_content": audio_b64_content}
        
        # --- Run Tests ---
        vad_asr_result = test_service("VAD & ASR Service", VAD_ASR_URL, audio_payload)
        test_service("Feature Extraction Service", EXTRACT_FEATURES_URL, audio_payload)
        test_service("Speech Emotion Recognition Service", ANALYZE_SER_URL, audio_payload)
        
        # Test Sentiment Analysis (only if ASR was successful)
        if vad_asr_result and "transcription" in vad_asr_result and vad_asr_result["transcription"]:
            sentiment_payload = {"text": vad_asr_result["transcription"]}
            test_service("Sentiment Analysis Service", SENTIMENT_URL, sentiment_payload) # This line caused the error
            
            similarity_payload = {"text1": vad_asr_result["transcription"], "text2": REFERENCE_SCRIPT}
            test_service("Similarity Service", SIMILARITY_URL, similarity_payload)

            prosody_payload = {
                "audio_content": audio_b64_content, 
                "transcription": vad_asr_result["transcription"]
            }
            test_service("Prosody Analysis Service", PROSODY_URL, prosody_payload)
        else:
             print("--- SKIPPING: Sentiment, Similarity & Prosody Services ---")
             print("Could not run because ASR service did not return a transcription.")
             print("-" * 30 + "\n")

    print("🏁 Test complete.")