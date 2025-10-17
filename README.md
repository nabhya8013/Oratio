# Oratio

A system for computational oratory synthesis and cognitive response evaluation.


## About The Project

Oratio is an advanced system designed to help users improve their public speaking and oratory skills. It leverages a suite of computational tools to analyze various facets of a speech, from the spoken words to the emotional tone. By providing a simulated environment and detailed feedback, Oratio aims to be a comprehensive training platform for speakers of all levels.

The project is built with a microservice-based architecture, with distinct layers for presentation, processing, and analysis, making it a robust and scalable solution.

## Features

  * **Speech-to-Text Transcription:** Converts spoken language into text for analysis.
  * **Voice Activity Detection (VAD):** Detects the presence of speech in an audio stream.
  * **Speech Emotion Recognition (SER):** Analyzes the emotional tone of the speaker's voice.
  * **Acoustic Feature Extraction:** Analyzes pitch and intensity to gauge vocal delivery.
  * **Similarity Analysis:** Compares the user's speech to a script or reference text.
  * **Interactive 3D Environment:** A Unity-based application provides a virtual stage for users to practice their speeches.

-----

## Architecture

Oratio's architecture is divided into the following layers:

  * **`ApplicationLayer`:** The frontend of the system, developed in Unity. This layer provides an interactive 3D environment for users to deliver their speeches.

  * **`PreSpeechLayer`:** A Go-based backend that manages user sessions and prepares the system for speech analysis. It interacts with external services like Gemini and Supabase for additional functionalities.

  * **`PostSpeechLayer`:** This layer is responsible for the post-analysis of the speech, including cognitive response evaluation.

  * **`Python Services`:** A collection of Python-based microservices, built with **FastAPI**, that form the core of Oratio's speech analysis capabilities:

      * **`vad_asr_service`**: Handles Voice Activity Detection and Automatic Speech Recognition using `speechbrain/vad-crdnn-libriparty` and `speechbrain/asr-crdnn-rnnlm-librispeech`.
      * **`extract_features_service`**: Extracts pitch and intensity features using the `parselmouth` library.
      * **`analyze_ser_service`**: Performs Speech Emotion Recognition using `speechbrain/emotion-recognition-wav2vec2-IEMOCAP`.
      * **`analyze_similarity_service`**: Analyzes the semantic similarity between texts using the `all-MiniLM-L6-v2` sentence transformer model.

-----

## Getting Started

This guide focuses on setting up and running the Python backend services.

### Prerequisites

  * Python 3.8+
  * `pip` and `venv`

### Installation and Setup

1.  **Clone the repo**

    ```sh
    git clone https://github.com/nabhya8013/oratio.git
    cd oratio
    ```

2.  **Set up the Python Virtual Environment**

    ```sh
    # Navigate to the Python services directory
    cd python_services

    # Create a virtual environment
    python -m venv venv

    # Activate the virtual environment
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    Create a file named `requirements.txt` inside the `python_services` directory and add the following:

    ```txt
    fastapi
    uvicorn[standard]
    pydantic
    speechbrain
    torch
    torchaudio
    parselmouth
    numpy
    sentence_transformers
    ```

    Then, install the packages:

    ```sh
    pip install -r requirements.txt
    ```

4.  **Model Caching (Important for Windows)**
    The first time you run the services, `SpeechBrain` will download pre-trained models. On Windows, this may fail due to permissions for creating symbolic links. To resolve this:

      * **Option A (Recommended):** Run your terminal (PowerShell, CMD, etc.) as an **Administrator**.
      * **Option B:** Enable **Developer Mode** in your Windows settings.

### Running the Services

You need to run each of the four services in a **separate terminal**. Make sure your virtual environment is activated in each one.

  * **Terminal 1: VAD & ASR Service**

    ```sh
    cd python_services/vad_asr_service
    uvicorn app:app --host 0.0.0.0 --port 8000
    ```

  * **Terminal 2: Feature Extraction Service**

    ```sh
    cd python_services/extract_features_service
    uvicorn app:app --host 0.0.0.0 --port 8001
    ```

  * **Terminal 3: Speech Emotion Recognition Service**

    ```sh
    cd python_services/analyze_ser_service
    uvicorn app:app --host 0.0.0.0 --port 8002
    ```

  * **Terminal 4: Similarity Service**

    ```sh
    cd python_services/analyze_similarity_service
    uvicorn app:app --host 0.0.0.0 --port 8003
    ```

At this point, all backend microservices are live and ready to accept requests.

-----

## API Endpoints

The services expect the raw audio file content to be sent as a **base64 encoded string**.

### 1\. VAD & ASR Service

  * **Endpoint:** `POST http://localhost:8000/vad_asr`
  * **Request Body:**
    ```json
    {
      "audio_content": "<base64_encoded_wav_file_content>"
    }
    ```
  * **Success Response (200 OK):**
    ```json
    {
      "start_time": 3.8999998569488525,
      "transcription": "ALL RIGHT ALL RIGHT SETTLE DOWN KIDS"
    }
    ```

### 2\. Feature Extraction Service

  * **Endpoint:** `POST http://localhost:8001/extract_features`
  * **Request Body:**
    ```json
    {
      "audio_content": "<base64_encoded_wav_file_content>"
    }
    ```
  * **Success Response (200 OK):**
    ```json
    {
        "pitch_mean": 172.63,
        "pitch_std": 58.21,
        "intensity_mean": 63.62,
        "intensity_std": 12.54
    }
    ```

### 3\. Speech Emotion Recognition Service

  * **Endpoint:** `POST http://localhost:8002/ser`
  * **Request Body:**
    ```json
    {
      "audio_content": "<base64_encoded_wav_file_content>"
    }
    ```
  * **Success Response (200 OK):**
    ```json
    {
      "label": "neu",
      "score": 12.609233856201172
    }
    ```

### 4\. Similarity Service

  * **Endpoint:** `POST http://localhost:8003/similarity`
  * **Request Body:**
    ```json
    {
      "text1": "ALL RIGHT ALL RIGHT SETTLE DOWN KIDS",
      "text2": "the quick brown fox jumps over the lazy dog"
    }
    ```
  * **Success Response (200 OK):**
    ```json
    {
      "similarity": 0.08838991075754166
    }
    ```

-----

## Testing the Backend

A test script is provided to verify that all services are running correctly.

1.  **Create the Test File:** In the root directory of the project (`oratio/`), create a file named `test_services.py`.

2.  **Add the Code:** Copy and paste the following code into `test_services.py`.

    ```python
    import requests
    import os
    import base64

    # --- CONFIGURATION ---
    # IMPORTANT: Update this with the full path to a .wav file on your system
    TEST_AUDIO_FILE = "D:\\AI PROJECT\\Oratio\\clips\\q1_16k.wav"
    REFERENCE_SCRIPT = "the quick brown fox jumps over the lazy dog"

    # --- SERVICE URLS ---
    VAD_ASR_URL = "http://localhost:8000/vad_asr"
    EXTRACT_FEATURES_URL = "http://localhost:8001/extract_features"
    ANALYZE_SER_URL = "http://localhost:8002/ser"
    SIMILARITY_URL = "http://localhost:8003/similarity"

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
            with open(TEST_AUDIO_FILE, "rb") as f:
                audio_bytes = f.read()
                audio_b64_content = base64.b64encode(audio_bytes).decode('utf-8')
            
            audio_payload = {"audio_content": audio_b64_content}
            
            vad_asr_result = test_service("VAD & ASR Service", VAD_ASR_URL, audio_payload)
            test_service("Feature Extraction Service", EXTRACT_FEATURES_URL, audio_payload)
            test_service("Speech Emotion Recognition Service", ANALYZE_SER_URL, audio_payload)

            if vad_asr_result and "transcription" in vad_asr_result and vad_asr_result["transcription"]:
                transcribed_text = vad_asr_result["transcription"]
                similarity_payload = {"text1": transcribed_text, "text2": REFERENCE_SCRIPT}
                test_service("Similarity Service", SIMILARITY_URL, similarity_payload)
            else:
                print("--- SKIPPING: Similarity Service ---")
                print("Could not run because ASR service did not return a transcription.")
                print("-" * 30 + "\n")

        print("🏁 Test complete.")
    ```

3.  **Run the Test:**
    Open a **new terminal** in the root project directory, activate the virtual environment, and run the script.

    ```sh
    python test_services.py
    ```

    If all services are running correctly, you will see a "✅ Success\!" message for each one.

-----
