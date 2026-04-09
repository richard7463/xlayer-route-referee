# X Layer Route Referee

Reusable execution-planning skill for X Layer agents.

`X Layer Route Referee` is built for the **OKX Build X Hackathon Skills Arena**.
It helps any agent decide whether a swap should be executed, which route should be preferred, and how much route risk is hidden behind the best quote.

## One-Line Pitch

Give any agent a swap intent and Route Referee returns the best route, fallback routes, route concentration risk, price impact context, and an execution recommendation.

## Why This Fits Skills Arena

This project is a reusable skill, not a full product shell.

Its job is narrow and valuable:

- compare DEX routes on X Layer
- score route quality and route fragility
- produce a structured recommendation another agent can execute
- explain the decision in agent-friendly and human-friendly form

That maps directly to the Skills Arena requirement: build a capability other agents can call.

## Core Skill Contract

Input:

- chain
- from token
- to token
- amount
- slippage tolerance
- optional preferred DEX list
- optional banned DEX list

Output:

- best route candidate
- ranked alternative routes
- route concentration score
- price impact assessment
- execution verdict: `execute`, `reduce-size`, or `skip`
- explanation block suitable for agent logs or Moltbook posts

## Project Intro

Most agent execution stacks stop at `best quote wins`.
That is not enough.

A route can have the best quoted output while still being fragile because of:

- high price impact
- single-route concentration
- dependence on one liquidity venue
- poor fallback coverage
- size sensitivity

Route Referee exists to turn raw quote data into a decision object another agent can trust.

## Architecture Overview

There are four layers:

1. `route_referee.client.OnchainOSClient`
   - signs and sends requests to OnchainOS DEX endpoints
   - fetches supported tokens, liquidity sources, and quotes

2. `route_referee.referee.RouteReferee`
   - expands a swap intent into route candidates
   - compares per-DEX and blended route options
   - computes route-quality and route-risk scores

3. `route_referee.models`
   - typed request and response models
   - stable output shape for downstream agents

4. `route_referee.cli`
   - local CLI entrypoint for demos, screenshots, and agent testing

## Onchain OS / Uniswap Skill Usage

Current code is designed around official OnchainOS DEX surfaces:

- token discovery
- liquidity source discovery
- quote retrieval
- route comparison per DEX
- optional swap-planning handoff

The evaluation logic is meant to sit in front of execution.
Another agent can take the recommendation and call a wallet or swap skill afterward.

The project is also positioned to compete for `Best Uniswap integration` by explicitly comparing Uniswap against alternative X Layer routes whenever Uniswap liquidity is available in the OnchainOS source list.

## Working Mechanics

1. An agent provides a swap intent.
2. Route Referee resolves token metadata on X Layer.
3. It fetches available liquidity sources.
4. It requests a baseline quote.
5. It requests isolated candidate quotes for major venues when available.
6. It ranks routes by output, price impact, venue concentration, and fallback quality.
7. It returns a structured recommendation object.
8. The calling agent can then execute, resize, or skip.

## Example Output

```json
{
  "verdict": "execute",
  "recommended_dex": "Uniswap V3",
  "recommended_output": "104.283194",
  "route_risk": "medium",
  "price_impact_pct": "0.42",
  "fallback_count": 2,
  "reason": "Uniswap V3 produced the strongest output with acceptable impact and two viable fallback venues."
}
```

## Local Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 -m route_referee.cli \
  --from-token USDC \
  --to-token OKB \
  --amount 25
```

## Environment Variables

- `ONCHAINOS_API_KEY`
- `ONCHAINOS_API_SECRET`
- `ONCHAINOS_API_PASSPHRASE`
- `ONCHAINOS_CHAIN_INDEX=196`
- `ONCHAINOS_PROXY=http://127.0.0.1:7890`

The client also accepts the official Dev Portal variable names:

- `OKX_API_KEY`
- `OKX_SECRET_KEY`
- `OKX_PASSPHRASE`

## Live Validation

This repo has already been validated against real OnchainOS quote endpoints on **April 9, 2026**.

Live checks completed:

- `USDC -> OKB` returned a successful route comparison
- `USDC -> USDT` returned a successful route comparison
- `USDC -> WBTC` returned an honest `Insufficient liquidity` error

Proof files:

- [Live Validation Notes](/Users/yanqing/Documents/GitHub/miraix-interface/projects/xlayer-route-referee/docs/live-validation.md)
- [Live Proof JSON](/Users/yanqing/Documents/GitHub/miraix-interface/projects/xlayer-route-referee/examples/live-proof-2026-04-09.json)

## Demo Flow

1. Ask the skill for `25 USDC -> OKB`.
2. Show the ranked route candidates.
3. Show why the top route won.
4. Show when the skill downgrades a route to `reduce-size` or `skip`.

## Submission Positioning

This repo should be submitted to the **Skills Arena**, not the X Layer Arena.

Why:

- it is a reusable capability
- it has a clean invocation boundary
- any trading, treasury, or bounty agent can call it
- it can be demonstrated without a full product wrapper

## Team

- `richard7463` - solo builder

## Status

Already done:

- standalone repo structure
- reusable skill specification
- OnchainOS client layer
- route comparison engine
- CLI demo surface
- Skills Arena positioning docs

Still required before final submission:

- optional Uniswap-specific tuning for prize targeting
- public demo recording
- final X / Moltbook submission posts

## Docs

- [Skill Spec](/Users/yanqing/Documents/GitHub/miraix-interface/projects/xlayer-route-referee/SKILL.md)
- [Project Positioning](/Users/yanqing/Documents/GitHub/miraix-interface/projects/xlayer-route-referee/docs/project-positioning.md)
- [Skills Arena Checklist](/Users/yanqing/Documents/GitHub/miraix-interface/projects/xlayer-route-referee/docs/skills-arena-checklist.md)
- [Live Validation](/Users/yanqing/Documents/GitHub/miraix-interface/projects/xlayer-route-referee/docs/live-validation.md)
- [Submission Post](/Users/yanqing/Documents/GitHub/miraix-interface/projects/xlayer-route-referee/docs/submission-post.md)
