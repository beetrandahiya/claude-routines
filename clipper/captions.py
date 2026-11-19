"""Build an ASS subtitle file: word-by-word captions plus a hook line.

Style: big white bold text with a thick black outline. The word being
spoken turns yellow. 1-3 words on screen at a time.
"""
from __future__ import annotations

import re

from .transcribe import Word

W, H = 1080, 1920

HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Display Black,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,3,5,40,40,0,1
Style: Hook,Inter Display ExtraBold,64,&H00000000,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,3,18,0,8,70,70,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

YELLOW = r"{\c&H00E5FF&}"  # ASS colours are BGR: this is #FFE500
WHITE = r"{\c&HFFFFFF&}"


def ts(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def clean(text: str) -> str:
    text = text.replace("{", "(").replace("}", ")").replace("\\", "")
    return text.upper()


def chunk_words(words: list[Word], max_words: int = 3, max_chars: int = 16, max_gap: float = 0.6) -> list[list[Word]]:
    chunks: list[list[Word]] = []
    cur: list[Word] = []
    for w in words:
        if cur:
            text_len = sum(len(x.text) + 1 for x in cur) + len(w.text)
            gap = w.start - cur[-1].end
            ends_sentence = bool(re.search(r"[.!?]$", cur[-1].text))
            if len(cur) >= max_words or text_len > max_chars or gap > max_gap or ends_sentence:
                chunks.append(cur)
                cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks


def build_ass(words: list[Word], hook: str | None, caption_y: int, hook_secs: float = 3.0,
              clip_len: float | None = None, hook_y: int = 90) -> str:
    """words: timestamps relative to the clip start."""
    out = [HEADER.format(w=W, h=H)]
    pos = rf"{{\pos({W // 2},{caption_y})}}"
    for chunk in chunk_words(words):
        for i, w in enumerate(chunk):
            start = w.start
            # hold each state until the next word starts (no flicker)
            end = chunk[i + 1].start if i + 1 < len(chunk) else w.end + 0.25
            parts = []
            for j, x in enumerate(chunk):
                parts.append((YELLOW if j == i else WHITE) + clean(x.text))
            text = pos + " ".join(parts)
            out.append(f"Dialogue: 1,{ts(start)},{ts(end)},Cap,,0,0,0,,{text}")
    if hook:
        end = min(hook_secs, clip_len) if clip_len else hook_secs
        htext = rf"{{\pos({W // 2},{hook_y})\fad(0,200)}}" + hook.replace("{", "(").replace("}", ")")
        out.append(f"Dialogue: 2,{ts(0)},{ts(end)},Hook,,0,0,0,,{htext}")
    return "\n".join(out) + "\n"
