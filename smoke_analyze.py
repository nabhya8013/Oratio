#!/usr/bin/env python3
"""
Small utility to exercise the Go /session/analyze endpoint.

Usage:
  python smoke_analyze.py --session-id 123 --audio path/to/audio.wav [--host http://localhost:8080]

Notes:
- Assumes the Go server is running on :8080
- The Python unified router should be running on :8000 (called by the Go server)
- This script only triggers analysis; it does not create a session
"""
import argparse
import base64
import json
import sys
import urllib.request


def post_json(url: str, payload: dict) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, body
    except Exception as e:
        return 0, str(e)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--session-id", type=int, required=True, help="Existing session ID to analyze")
    p.add_argument("--audio", required=True, help="Path to a small .wav/.mp3 file")
    p.add_argument("--host", default="http://localhost:8080", help="Go API host (default: http://localhost:8080)")
    args = p.parse_args()

    try:
        with open(args.audio, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("ascii")
    except Exception as e:
        print(f"Failed to read audio file: {e}")
        return 1

    url = args.host.rstrip("/") + "/session/analyze"
    payload = {"session_id": args.session_id, "audio_base64": audio_b64}

    print(f"POST {url} ...")
    status, body = post_json(url, payload)
    print(f"Status: {status}")

    if isinstance(body, dict):
        print(json.dumps(body, indent=2)[:4000])  # truncate just in case
        # Quick peek if transcript exists
        vad = body.get("vad_asr") or {}
        if isinstance(vad, dict) and "transcription" in vad:
            print("\nTranscript preview:", vad["transcription"][:200])
    else:
        print(body[:4000])

    return 0 if status and 200 <= status < 300 else 1


if __name__ == "__main__":
    sys.exit(main())

