"""Speech to text with word timestamps (faster-whisper).

On the PC use model="large-v3-turbo", device="cuda".
On a CPU box use model="small" or "base" for speed.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Word:
    start: float
    end: float
    text: str


def pick_device() -> tuple[str, str]:
    """Return (device, compute_type). Uses the GPU when CUDA is there."""
    try:
        import ctranslate2

        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "int8"


def load_audio(path: str, sr: int = 16000):
    """Decode any audio/video file to 16 kHz mono float32 with ffmpeg."""
    import subprocess

    import numpy as np

    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(sr),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def transcribe_words(path: str, model: str | None = None, language: str = "en") -> list[Word]:
    from faster_whisper import WhisperModel

    device, compute = pick_device()
    if model is None:
        model = "large-v3-turbo" if device == "cuda" else "small"
    wm = WhisperModel(model, device=device, compute_type=compute)
    segments, _info = wm.transcribe(
        load_audio(path),
        language=language,
        word_timestamps=True,
        vad_filter=True,
        beam_size=5 if device == "cuda" else 1,
    )
    words: list[Word] = []
    for seg in segments:
        for w in seg.words or []:
            t = w.word.strip()
            if t:
                words.append(Word(float(w.start), float(w.end), t))
    return words
