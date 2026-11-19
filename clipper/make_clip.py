"""Make one vertical clip.

  python -m clipper.make_clip --src stream.mp4 --start 120 --end 150 --hook "HE DID NOT SEE THAT COMING" --out out.mp4
  python -m clipper.make_clip --src https://www.twitch.tv/videos/123 --start 3600 --end 3630 --out out.mp4

A URL source downloads only the needed slice (yt-dlp --download-sections).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import time

from .render import REPO, render_clip


def fetch_slice(url: str, start: float, end: float, workdir: str) -> str:
    os.makedirs(workdir, exist_ok=True)
    tmpl = os.path.join(workdir, "slice_%(id)s_" + f"{int(start)}.%(ext)s")
    r = subprocess.run(["yt-dlp", "-q", "--no-warnings", "-f", "best[height<=1080]/best",
                        "--download-sections", f"*{start}-{end}", "--force-keyframes-at-cuts",
                        "-o", tmpl, "--print", "after_move:filepath", url],
                       capture_output=True, text=True, check=True)
    return r.stdout.strip().splitlines()[-1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="video file or URL")
    ap.add_argument("--start", type=float, required=True)
    ap.add_argument("--end", type=float, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--hook")
    ap.add_argument("--streamer")
    ap.add_argument("--whisper-model")
    a = ap.parse_args()

    src, start, end = a.src, a.start, a.end
    if src.startswith("http"):
        src = fetch_slice(src, start, end, os.path.join(REPO, "work"))
        start, end = 0.0, end - start
    t0 = time.time()
    res = render_clip(src, start, end, a.out, hook=a.hook, streamer=a.streamer, whisper_model=a.whisper_model)
    print(f"done in {time.time() - t0:.1f}s  layout={res.layout}  encoder={res.encoder}  "
          f"facecam={res.facecam}  words={len(res.words)}  -> {res.out}")


if __name__ == "__main__":
    main()
