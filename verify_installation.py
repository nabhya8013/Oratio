import importlib
import torch

def check_library(library_name):
    """Checks if a library is installed and prints a status message."""
    try:
        importlib.import_module(library_name)
        print(f"✅  Successfully imported '{library_name}'")
        return True
    except ImportError:
        print(f"❌  Failed to import '{library_name}'. Please make sure it is installed.")
        return False

def main():
    """Main function to run all checks."""
    print("🚀  Starting Oratio Python services verification...\n")

    # --- Library Checks ---
    print("🔍  Checking required libraries...")
    libraries = [
        "fastapi", "pydantic", "speechbrain", "torch", "torchaudio",
        "parselmouth", "numpy", "sentence_transformers", "uvicorn"
    ]
    all_libraries_installed = all(check_library(lib) for lib in libraries)

    if not all_libraries_installed:
        print("\n🚫  Some libraries are missing. Please install them using 'pip install -r requirements.txt'")
        return

    print("\n✅  All required libraries are installed.\n")

    # --- Model Checks ---
    print("🔍  Checking and downloading pre-trained models (this may take a while)...")
    try:
        print("\n--- VAD & ASR Service ---")
        from speechbrain.pretrained import VAD, EncoderDecoderASR
        print("Downloading VAD model...")
        VAD.from_hparams(source="speechbrain/vad-crdnn-libriparty")
        print("✅  VAD model loaded successfully.")
        print("Downloading ASR model...")
        EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-rnnlm-librispeech", savedir="pretrained_models/asr-crdnn-rnnlm-librispeech")
        print("✅  ASR model loaded successfully.")

        print("\n--- SER Service ---")
        from speechbrain.inference import EncoderClassifier
        print("Downloading SER model...")
        # Corrected the model source below
        EncoderClassifier.from_hparams(source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP", savedir="pretrained_models/emotion-recognition-wav2vec2-IEMOCAP")
        print("✅  SER model loaded successfully.")

        print("\n--- Similarity Service ---")
        from sentence_transformers import SentenceTransformer
        print("Downloading Sentence Transformer model...")
        SentenceTransformer('all-MiniLM-L6-v2')
        print("✅  Sentence Transformer model loaded successfully.")

    except Exception as e:
        print(f"\n❌  An error occurred while loading a model: {e}")
        print("Please check your internet connection and try again.")
        return

    print("\n\n🎉  All checks passed! Your environment is ready for the Oratio Python services.")

if __name__ == "__main__":
    main()