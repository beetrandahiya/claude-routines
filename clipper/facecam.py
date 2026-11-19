"""Find the streamer's facecam in a 16:9 stream.

Samples frames, finds faces with OpenCV's built-in Haar detector (no
download), takes the median face, and returns a crop box around it with
the aspect ratio of the top panel. A per-streamer override in
layouts.json beats auto-detection.
"""
from __future__ import annotations

import json
import os
import statistics
from dataclasses import dataclass

import cv2


@dataclass
class Box:
    x: int
    y: int
    w: int
    h: int


def _even(v: float) -> int:
    return int(v) // 2 * 2


def sample_faces(path: str, start: float, end: float, n: int = 12) -> list[tuple[int, int, int, int]]:
    cap = cv2.VideoCapture(path)
    det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = []
    for i in range(n):
        t = start + (end - start) * (i + 0.5) / n
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fh = frame.shape[0]
        found = det.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(fh // 20, fh // 20))
        if len(found):
            # the facecam face is usually the biggest real face on screen
            x, y, w, h = max(found, key=lambda f: f[2] * f[3])
            faces.append((int(x), int(y), int(w), int(h)))
    cap.release()
    return faces


def detect_facecam(path: str, start: float, end: float, aspect: float, frame_w: int, frame_h: int,
                   scale: float = 3.2) -> Box | None:
    faces = sample_faces(path, start, end)
    if len(faces) < 3:
        return None
    cx = statistics.median(x + w / 2 for x, y, w, h in faces)
    cy = statistics.median(y + h / 2 for x, y, w, h in faces)
    fw = statistics.median(w for x, y, w, h in faces)
    bw = min(fw * scale, frame_w)
    bh = bw / aspect
    if bh > frame_h:
        bh = frame_h
        bw = bh * aspect
    x = min(max(cx - bw / 2, 0), frame_w - bw)
    y = min(max(cy - bh * 0.45, 0), frame_h - bh)  # face a bit above centre
    return Box(_even(x), _even(y), _even(bw), _even(bh))


def load_override(streamer: str | None, frame_w: int, frame_h: int, layouts_path: str = "layouts.json") -> Box | None:
    """layouts.json: {"kaicenat": {"facecam": [x, y, w, h]}} in fractions of the frame (0-1)."""
    if not streamer or not os.path.exists(layouts_path):
        return None
    data = json.load(open(layouts_path))
    entry = data.get(streamer.lower())
    if not entry or "facecam" not in entry:
        return None
    fx, fy, fw, fh = entry["facecam"]
    return Box(_even(fx * frame_w), _even(fy * frame_h), _even(fw * frame_w), _even(fh * frame_h))
