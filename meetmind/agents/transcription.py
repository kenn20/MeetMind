import base64
import os
import requests
import railtracks as rt


def _openrouter_headers():
    key = os.getenv("OpenRouterKey")
    if not key:
        raise RuntimeError("ERROR: OpenRouterKey env var not set")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


@rt.function_node
def transcribe_meeting(audio_path: str):
    """Transcribe a meeting audio or video file with speaker diarization.

    Args:
        audio_path (str): Absolute or relative path to the audio/video file (mp3, wav, m4a, mp4, etc.)
    """
    if not os.path.exists(audio_path):
        return f"ERROR: File not found: {audio_path}"

    with open(audio_path, "rb") as f:
        base64_audio = base64.b64encode(f.read()).decode("utf-8")

    ext = audio_path.rsplit(".", 1)[-1].lower()
    if ext == "mp4":
        ext = "mp4"

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=_openrouter_headers(),
        json={
            "model": "google/gemini-2.5-flash",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Transcribe this meeting audio with speaker diarization.\n"
                                "Format each line as: [HH:MM:SS] Speaker N: <what they said>\n"
                                "Label each unique speaker as Speaker 1, Speaker 2, etc.\n"
                                "Include a new line whenever the speaker changes.\n"
                                "If a speaker's name is mentioned in the conversation, note it in parentheses "
                                "e.g. Speaker 1 (Marcus).\n"
                                "Transcribe everything verbatim."
                            ),
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {"data": base64_audio, "format": ext},
                        },
                    ],
                }
            ],
        },
        timeout=120,
    )
    data = response.json()
    if "choices" not in data:
        return f"ERROR: OpenRouter response: {str(data)[:300]}"
    return data["choices"][0]["message"]["content"]
