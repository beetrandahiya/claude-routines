# GTA 6 auto-clipper

Goal: find the best moments in other people's GTA 6 streams, cut them into captioned vertical clips, approve from a phone, post to YouTube Shorts, Instagram Reels and TikTok, and track views and earnings. Money comes mainly from clipping campaigns (Content Rewards / Whop).

Hard limits: no spending, no paid APIs, local models only.

Machines:
- Windows PC (RTX 4070 Ti, 32 GB): heavy work. Mostly on.
- MacBook M1 (8 GB): always on. Runs the queue, scheduler and web UI.
- They talk over Tailscale.

Research: see docs/research-2026-11.md

## Decisions log
- 2026-11-19: Country is Germany. TikTok and TikTok Creator Rewards are available.
- 2026-11-19: Fresh accounts, one per platform. Many duplicate accounts get hit by the reach penalties for reposted clips.
- 2026-11-19: Approve clips on a web page over Tailscale (user's choice over a Telegram bot).
- 2026-11-19: 10-20 min of hands-on time per day.
- 2026-11-19: English first. German is deferred.
- 2026-11-19: Clip styles: funny/fails, discoveries/tips, big-streamer hype, plus learning from results.
- 2026-11-19: Campaigns first. Platform programs come later.
- 2026-11-19: User said go. Building started.
- 2026-11-19: Twitch data comes only from the official Helix API with the user's own free dev app. A call to Twitch's internal website API was blocked, which is correct.
- 2026-11-19: Chat replay only exists through Twitch's internal API (TwitchDownloader uses it). Chat spikes are on hold until the user decides. Start with top clips, audio and the LLM instead.
- 2026-11-19: Caption font is Inter Display (free OFL licence), shipped in fonts/ so Windows and the Mac render the same.
- 2026-11-19: faster-whisper gets audio decoded by ffmpeg (numpy array), not its own PyAV reader, which broke on version mismatch.

## Cancelled / rejected
- Browser-automation posting: breaks TikTok and Meta terms, ban risk.
- TikTok API audit: TikTok's own guidelines exclude this use case. Use inbox drafts or a manual share instead.
- German-first content: deferred, not cancelled.

## Status
- Slice 0 test 3 (render) works on CPU: a 36s clip took 33s with whisper small. Not yet timed on the PC with NVENC.
- Known issues:
  - The game's own subtitles get cut off at the gameplay crop edges.
  - Auto facecam crop can catch a bit of gameplay next to the cam.
  - Story cutscenes are not detected yet. That is the Rockstar takedown risk.
- Waiting for: Twitch dev app (test 1), developer accounts for posting tests (test 2).

## How to run
Setup (Windows PC or Mac). Needs Python 3.11+ and ffmpeg on PATH:
    pip install -r requirements.txt
Make one clip from a file or a URL (URL downloads only that slice):
    python -m clipper.make_clip --src https://www.twitch.tv/videos/ID --start 3600 --end 3630 --hook "HOOK TEXT" --out clip.mp4
- Uses NVENC and Whisper large-v3-turbo on the GPU automatically. Falls back to libx264 and Whisper small on CPU.
- To pin a streamer's facecam box, add layouts.json at the repo root: {"name": {"facecam": [x, y, w, h]}}. Values are fractions of the frame.
