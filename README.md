# X Layer Route Referee

![Track](https://img.shields.io/badge/Track-Build%20X%20Skills%20Arena-0f766e)
![Skill](https://img.shields.io/badge/Skill-Pre--Execution%20Referee-111827)
![Network](https://img.shields.io/badge/Network-X%20Layer%20196-2563eb)
![Proof](https://img.shields.io/badge/Live%20Proof-Apr%2013%202026-success)

Reusable pre-execution referee skill for autonomous X Layer agents.

> Best quote is not enough. Agents need a referee before they trade.

## Judge Summary

| What judges should look for | Evidence |
| --- | --- |
| Reusable Skills Arena primitive | Any trading, treasury, payment, or bounty agent can call it before swap execution. |
| OnchainOS integration | Uses live OnchainOS token discovery, liquidity-source discovery, and quote endpoints on X Layer. |
| Agent decision surface | Converts route data into `execute`, `resize`, `retry`, or `block`. |
| Proof-oriented output | Every evaluation includes checks, decision rationale, route candidates, and `proof_id`. |
| Honest failure handling | Captures insufficient-liquidity cases instead of hiding them. |
| X Layer ecosystem fit | Built around chain index `196`, X Layer DEX venues, Uniswap routes, and Agentic Wallet submission identity. |

## One-Line Pitch

X Layer Route Referee turns an agent trade intent into a pre-execution verdict: execute, resize, retry, or block.

## Why This Exists

Most agent execution stacks stop at:

```text
fetch quote -> pick best output -> execute
```

That is too weak for autonomous agents. A route can have the best quoted output while still being fragile because of:

- high price impact
- single-route concentration
- no fallback venue
- banned or unwanted venues
- low-liquidity tails
- missing execution reason

Route Referee sits immediately before swap execution and answers the real question:

```text
should this agent execute this route right now?
```

## Core Skill Contract

Input: agent trade intent.

```json
{
  "agent_name": "flasharb",
  "intent_id": "arb-probe-104",
  "from_token": "USDC",
  "to_token": "OKB",
  "amount": "25",
  "slippage_percent": "0.5",
  "preferred_dexes": ["Uniswap V3"],
  "banned_dexes": [],
  "reason": "pre-execution route quality check",
  "max_price_impact_percent": "1.20",
  "min_fallback_count": 1
}
```

Output: route proof and verdict.

```json
{
  "verdict": "execute",
  "route_risk": "medium",
  "proof_id": "route_referee_66ae6fe48c673a5f",
  "decision": {
    "action": "execute",
    "risk_level": "medium",
    "recommended_size_multiplier": "1.00",
    "policy_hits": ["route_within_referee_limits"]
  },
  "checks": [
    {"id": "quote_available", "ok": true},
    {"id": "price_impact", "ok": true},
    {"id": "fallback_coverage", "ok": true},
    {"id": "banned_dex_exclusion", "ok": true},
    {"id": "agent_reason", "ok": true}
  ]
}
```

## Decision Actions

| Action | Meaning |
| --- | --- |
| `execute` | Route is acceptable under current quote, impact, fallback, and policy checks. |
| `resize` | Route exists, but size should be reduced before execution. |
| `retry` | Route is not safe enough now; try again or ask another venue/source. |
| `block` | Route should not execute. |

## Live Validation

Latest proof was captured against live OnchainOS quote endpoints on **April 13, 2026**.

| Pair | Result | Verdict / Error | Proof |
| --- | --- | --- | --- |
| `USDC -> OKB` | success | `execute`, medium risk | `route_referee_66ae6fe48c673a5f` |
| `USDC -> USDT` | success | `execute`, low risk | `route_referee_c6c38d0ef9b68647` |
| `USDC -> WBTC` | honest failure | `OKX API error 82000: Insufficient liquidity` | captured in proof JSON |

Proof files:

- [`examples/live-proof-latest.json`](examples/live-proof-latest.json)
- [`examples/live-proof-2026-04-13.json`](examples/live-proof-2026-04-13.json)
- [`docs/live-validation.md`](docs/live-validation.md)

## Architecture

```text
agent trade intent
  -> token resolver
  -> OnchainOS liquidity source discovery
  -> aggregated quote
  -> isolated venue quotes
  -> route risk scoring
  -> policy checks
  -> execute / resize / retry / block decision
  -> proof packet for logs, Moltbook, or downstream agents
```

Code layout:

| Layer | Path | Purpose |
| --- | --- | --- |
| Skill spec | [`SKILL.md`](SKILL.md) | Agent-facing invocation contract. |
| Models | [`route_referee/models.py`](route_referee/models.py) | Typed request, route, checks, decision, response. |
| Referee engine | [`route_referee/referee.py`](route_referee/referee.py) | Scores routes and creates pre-execution verdicts. |
| OnchainOS client | [`route_referee/client.py`](route_referee/client.py) | HMAC-signed access to OKX / OnchainOS DEX endpoints. |
| CLI | [`route_referee/cli.py`](route_referee/cli.py) | Local and OpenClaw demo entrypoint. |
| Live capture | [`scripts/capture_live_demo.py`](scripts/capture_live_demo.py) | Generates dated proof JSON from live endpoints. |

## OnchainOS / Uniswap Usage

Route Referee uses official OnchainOS DEX surfaces:

- token discovery: `/api/v6/dex/aggregator/all-tokens`
- liquidity sources: `/api/v6/dex/aggregator/get-liquidity`
- route quotes: `/api/v6/dex/aggregator/quote`
- Uniswap comparison: preferred route can explicitly include `Uniswap V3`; live source list includes Uniswap V2, Uniswap V3, Uniswap V4, and Uniswap hook routes when available

The skill does not custody funds. It is designed to sit before an Agentic Wallet / swap skill.

## Onchain Identity

- network: `X Layer`
- chain index: `196`
- submission wallet: `0xdbc8e35ea466f85d57c0cc1517a81199b8549f04`
- deployment model: offchain reusable skill with OnchainOS quote access and Agentic Wallet identity for hackathon submission

## Local Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 -m pytest -q
python3 -m route_referee.cli \
  --agent flasharb \
  --intent-id arb-probe-104 \
  --from-token USDC \
  --to-token OKB \
  --amount 25 \
  --prefer-dex "Uniswap V3" \
  --reason "pre-execution route quality check"
```

## Environment Variables

Required for live OnchainOS validation:

- `ONCHAINOS_API_KEY` or `OKX_API_KEY`
- `ONCHAINOS_API_SECRET` or `OKX_SECRET_KEY`
- `ONCHAINOS_API_PASSPHRASE` or `OKX_PASSPHRASE`
- `ONCHAINOS_CHAIN_INDEX=196`

Optional on local Mac:

- `ONCHAINOS_PROXY=http://127.0.0.1:7890`

OpenClaw/server usually should not set a proxy unless required.

## Demo Flow

1. Show an agent trade intent: `USDC -> OKB`.
2. Run the CLI and show `execute / resize / retry / block` output.
3. Open `examples/live-proof-latest.json`.
4. Show the honest failure case for `USDC -> WBTC`.
5. Explain that another agent can use this verdict before calling Agentic Wallet execution.

## Submission Positioning

This repo should be submitted to the **Skills Arena**.

It is not a trading bot. It is a reusable pre-execution referee that improves agent reliability across trading, treasury, payment, and DeFi workflows.

## Team

- `richard7463` - solo builder

## Status

Done:

- public GitHub repo
- reusable skill specification
- OnchainOS client layer
- pre-execution referee model
- route comparison engine
- CLI demo surface
- live quote validation proof
- Skills Arena docs
- Moltbook / X draft posts

Manual submission assets to attach after repo push:

- public demo recording
- final Moltbook post link
- final X post link
- Google Form submission

## Docs

- [`SKILL.md`](SKILL.md)
- [`docs/project-positioning.md`](docs/project-positioning.md)
- [`docs/skills-arena-checklist.md`](docs/skills-arena-checklist.md)
- [`docs/live-validation.md`](docs/live-validation.md)
- [`docs/submission-post.md`](docs/submission-post.md)
- [`docs/submission-runbook.md`](docs/submission-runbook.md)
- [`docs/x-post.md`](docs/x-post.md)
