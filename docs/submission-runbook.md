# Submission Runbook

Use this checklist to push `X Layer Route Referee` from repo-ready to final Skills Arena submission.

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
  - latest proof links

## 2. Live Proof

Run:

```bash
python3 -m pytest -q
python3 scripts/capture_live_demo.py
```

Keep:

- `examples/live-proof-latest.json`
- `examples/live-proof-YYYY-MM-DD.json`

Current expected live checks:

- `USDC -> OKB`: successful pre-execution verdict
- `USDC -> USDT`: successful pre-execution verdict
- `USDC -> WBTC`: honest insufficient-liquidity failure case

## 3. Demo Video

Recommended 75-second structure:

1. Problem: best-quote-wins is not enough for autonomous agents.
2. Input: show one agent trade intent.
3. Output: show `execute / resize / retry / block` decision.
4. Proof: show `proof_id`, checks, and route candidates.
5. Honest failure: show insufficient-liquidity case.
6. Positioning: reusable pre-execution referee for X Layer agents.

## 4. Public Posts

- post the Moltbook submission using `docs/submission-post.md`
- publish the X post using `docs/x-post.md`

## 5. Google Form Links

Prepare:

- GitHub repo: `https://github.com/richard7463/xlayer-route-referee`
- README: `https://github.com/richard7463/xlayer-route-referee/blob/main/README.md`
- proof JSON: `https://github.com/richard7463/xlayer-route-referee/blob/main/examples/live-proof-latest.json`
- Moltbook post link
- X post link
- demo video link
