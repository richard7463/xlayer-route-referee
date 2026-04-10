# Submission Runbook

Use this checklist to push `X Layer Route Referee` from repo-ready to submission-ready.

## 1. Repo

- confirm `main` is pushed to the public GitHub repo
- confirm README includes:
  - project intro
  - architecture overview
  - usage surface
  - OnchainOS / Uniswap usage
  - working mechanics
  - team
  - X Layer ecosystem positioning
  - onchain identity

## 2. Live Proof

- run `python3 scripts/capture_live_demo.py`
- keep:
  - `examples/live-proof-latest.json`
  - the dated proof file for the run day
- capture one CLI screenshot for:
  - `USDC -> OKB`
  - `USDC -> USDT`
  - one honest failure case

## 3. Public Posts

- post the Moltbook submission using [submission-post.md](/Users/yanqing/Documents/GitHub/miraix-interface/projects/xlayer-route-referee/docs/submission-post.md)
- publish an X post with:
  - project name
  - repo link
  - screenshot
  - `#onchainos`
  - `@XLayerOfficial`

## 4. Submission Form

Prepare these links:

- GitHub repo
- README
- proof JSON
- Moltbook post
- X post
- demo video

## 5. Demo Video

Recommended 90-second structure:

1. problem: best-quote-wins is not enough
2. input: show one swap intent
3. output: show ranked routes and verdict
4. proof: show honest low-liquidity failure case
5. positioning: reusable execution judgment layer for X Layer agents
