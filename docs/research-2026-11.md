# Research notes (19 Nov 2026)

Gathered by web research on launch day. Anything marked (unverified) could not be confirmed and gets settled by a tiny test before we build on it.

## GTA 6
- Launches 19 Nov 2026, PS5 and Xbox Series only. No PC date yet. Metacritic 99.
- Rockstar video policy: fan videos are allowed for "non-commercial" use, and Take-Two can take anything down at any time.
  Banned: leaked footage, ending reveals, cutscene compilations, isolated cinematics, in-game TV shows.
  -> Never clip story cutscenes or spoilers. https://support.rockstargames.com/articles/200153756
- YouTube (Sep 2026): graphic game violence in the first 7 seconds makes a video not ad-eligible.

## Money
- Content Rewards (contentrewards.com, payouts via Whop):
  - How it works: link your accounts there, post to a campaign brief, submit the post link, get paid (views/1000) x rate up to a per-clip cap.
  - Median rate is about $1 per 1,000 views (gaming about $1.40). Fee 10%. Payouts every 7 days plus a 3-day hold. A clip stops earning 30 days after submission.
  - Every clip gets a bot score, and a human reviews every clip.
  - 1M views at $1 per 1,000 is about $900.
- GTA 6 campaigns live on 18 Nov: Kai Cenat ($10k pool), Lacy marathon ($12.5k pool), and others.
  Typical brief: 9:16, captions, facecam on top and gameplay below, tag the streamer, mute radio music, no spoilers.
- Other marketplaces exist: Vyro, Clipping.io, ClipFarm, streamer Discords. Rates $0.25-3 per 1,000 views.
  Kick streamer N3on paid about $0.45 per 1,000.
- Platform programs are hard to reach:
  - YouTube Partner Program (YPP): 1k subs + 10M Shorts views in 90 days. Rises to 20M from 1 Feb 2027.
  - TikTok Creator Rewards: 10k followers, videos 60s+, original content. Available in Germany (check in app).
  - Instagram: no general Reels payout.
- Reach penalties for reposted clips:
  - YouTube, Oct 2026: Shorts favour original content. Voiceover that only describes the clip, and template edits, don't count as original.
  - Instagram, Apr 2026: aggregator accounts are cut from recommendations.
  -> Add real value: context hook text, good captions, edits that tell a story. Use one account per platform, not dozens.

## Posting APIs
- YouTube Data API:
  - Since 2 Nov 2026, uploads from unverified projects can be public. (verify with a test)
  - Uploads have their own quota of 100 per day. A video is a Short if it is vertical and 3 minutes or less.
  - The OAuth app must be set to "In production", or the login expires after 7 days.
- Instagram API with Instagram Login:
  - Needs a Business or Creator account, no Facebook Page. 100 posts per 24h.
  - Development mode with yourself as tester should work without App Review. (verify with a test)
- TikTok Content Posting API:
  - Unaudited apps can only post privately (SELF_ONLY).
  - The audit excludes "copying content from other platforms" and "tools for your own accounts".
  - The plan is upload to inbox (draft), finished on the phone, or a manual share. (verify that inbox upload works unaudited)
- Browser-automation uploaders break TikTok and Meta terms and risk bans. Rejected.

## Finding moments
1. Twitch Helix Get Clips: sorted by views. Each clip has `vod_offset`, its timestamp in the VOD. This is the strongest and cheapest signal.
2. Chat velocity spikes against a rolling baseline, weighted by emotes (KEKW, LUL, W/L).
   Chat reacts late, so start the cut 15-30s before the spike. Get chat with TwitchDownloaderCLI (MIT).
3. YouTube "most replayed" heatmap (the yt-dlp `heatmap` field).
4. Audio loudness and scream peaks, as confirmation.
5. Transcript plus a local LLM (qwen3:14b or gemma4:12b via Ollama, JSON output) to rerank and write titles.
- Kick: yt-dlp does VODs and clips (needs curl_cffi). There is no chat history API, so record chat live over the WebSocket.
- Twitch VODs expire after about 7 days (60 for Partners), so download promptly.

## Tools
- faster-whisper (MIT): a 3h VOD takes about 2-4 min on the 4070 Ti (estimate). WhisperX (BSD) for word alignment.
- MediaPipe (Apache-2.0) for face detection. Avoid Ultralytics (AGPL).
- Gaming layout: find the facecam box once per streamer, then stack facecam on top and gameplay below with ffmpeg crop+vstack.
- Karaoke captions: ASS file built from word timestamps, burned with libass, encoded with h264_nvenc.
- mutonby/openshorts (MIT core) is a good reference for layouts and face tracking. It needs Gemini for auto-layout and uses paid posting, so we don't use it as-is.
