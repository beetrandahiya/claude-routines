"""Turn a slice of a 16:9 stream into a 1080x1920 clip.

Layout "stack": facecam on top (1080x700), gameplay below (1080x1220),
captions on the seam, hook line at the top for the first 3 seconds.
Layout "fill" (no facecam found): the full frame in the middle over a
blurred, zoomed copy of itself.
"""
from __future__ import annotations

import functools
import json
import os
import subprocess
from dataclasses import dataclass

from .captions import H, W, build_ass
from .facecam import Box, detect_facecam, load_override
from .transcribe import Word, transcribe_words

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(REPO, "fonts")
TOP_H = 700
BOT_H = H - TOP_H


@dataclass
class RenderResult:
    out: str
    layout: str
    facecam: Box | None
    words: list[Word]
    encoder: str


def probe(path: str) -> dict:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate", "-show_entries", "format=duration", "-of", "json", path],
        capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    s = d["streams"][0]
    return {"w": int(s["width"]), "h": int(s["height"]), "duration": float(d["format"]["duration"])}


@functools.lru_cache(maxsize=1)
def pick_encoder() -> str:
    """Use NVENC if the GPU really works, else libx264."""
    test = ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=black:s=256x256:d=0.1",
            "-c:v", "h264_nvenc", "-f", "null", "-"]
    try:
        if subprocess.run(test, capture_output=True, timeout=20).returncode == 0:
            return "h264_nvenc"
    except Exception:
        pass
    return "libx264"


def _ffpath(p: str) -> str:
    """Path safe for an ffmpeg filter argument (relative, forward slashes)."""
    rel = os.path.relpath(p, REPO).replace("\\", "/")
    return rel.replace(":", r"\:").replace("'", r"\'")


def extract_audio(src: str, start: float, end: float, wav: str) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-to", str(end), "-i", src,
                    "-vn", "-ac", "1", "-ar", "16000", wav], check=True)


def render_clip(src: str, start: float, end: float, out: str, hook: str | None = None,
                streamer: str | None = None, whisper_model: str | None = None,
                words: list[Word] | None = None, workdir: str | None = None) -> RenderResult:
    info = probe(src)
    fw, fh = info["w"], info["h"]
    end = min(end, info["duration"])
    length = end - start
    workdir = workdir or os.path.join(REPO, "work")
    os.makedirs(workdir, exist_ok=True)
    base = os.path.splitext(os.path.basename(out))[0]

    if words is None:
        wav = os.path.join(workdir, base + ".wav")
        extract_audio(src, start, end, wav)
        words = transcribe_words(wav, model=whisper_model)
        os.remove(wav)

    cam = load_override(streamer, fw, fh) or detect_facecam(src, start, end, W / TOP_H, fw, fh)
    layout = "stack" if cam else "fill"

    if layout == "stack":
        gw = int(fh * W / BOT_H) // 2 * 2
        gx = (fw - gw) // 2
        vf = (f"[0:v]split=2[a][b];"
              f"[a]crop={cam.w}:{cam.h}:{cam.x}:{cam.y},scale={W}:{TOP_H}:flags=lanczos,setsar=1[top];"
              f"[b]crop={gw}:{fh}:{gx}:0,scale={W}:{BOT_H}:flags=lanczos,setsar=1[bot];"
              f"[top][bot]vstack=inputs=2[v0]")
        caption_y = TOP_H
    else:
        vf = (f"[0:v]split=2[a][b];"
              f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.15[bg];"
              f"[b]scale={W}:-2:flags=lanczos[fg];"
              f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v0]")
        caption_y = int(H * 0.72)

    ass_path = os.path.join(workdir, base + ".ass")
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(build_ass(words, hook, caption_y, clip_len=length))
    vf += f";[v0]ass='{_ffpath(ass_path)}':fontsdir='{_ffpath(FONTS)}'[v]"

    enc = pick_encoder()
    venc = (["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "23", "-b:v", "0", "-maxrate", "12M", "-bufsize", "24M"]
            if enc == "h264_nvenc" else ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21"])
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-to", str(end), "-i", src,
           "-filter_complex", vf, "-map", "[v]", "-map", "0:a?",
           *venc, "-pix_fmt", "yuv420p", "-r", "30",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
           "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True, cwd=REPO)
    return RenderResult(out, layout, cam, words, enc)
