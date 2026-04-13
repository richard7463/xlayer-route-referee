# Project Positioning

X Layer Route Referee is a reusable pre-execution judgment skill for X Layer agents.

## Core Claim

Agents should not treat the highest quote as the only truth.
They need a referee before execution.

## What The Skill Does

- receives one agent trade intent
- compares route candidates
- scores route quality
- checks price impact, fallback coverage, banned venues, and reason presence
- returns one final verdict: `execute`, `resize`, `retry`, or `block`
- emits a proof ID and agent-ready explanation

## Why It Fits Skills Arena

This project is not a consumer app.
It is a modular capability that any agent can call before execution.

## Why It Is Stronger Than A Thin Quote Wrapper

A thin wrapper only returns numbers.
Route Referee returns:

- a decision
- a reason
- alternative routes
- route-quality checks
- execution caution when the quote is fragile
- honest failure proof when liquidity is insufficient

## Prize Strategy

Primary target:

- `Skills Arena`

Strong special-prize angles:

- `Best Uniswap integration`
- `Best data analyst`

The project can explicitly compare Uniswap against other X Layer venues and explain when Uniswap wins or loses. It also turns market route data into agent decisions.
