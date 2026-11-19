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

## Cancelled / rejected
- Browser-automation posting: breaks TikTok and Meta terms, ban risk.
- TikTok API audit: TikTok's own guidelines exclude this use case. Use inbox drafts or a manual share instead.
- German-first content: deferred, not cancelled.

## Status
- Questions done. Research done. Plan proposed, waiting for the user's go.

## How to run
- Nothing to run yet.
