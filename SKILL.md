---
name: xlayer-route-referee
description: Use this skill when an agent needs to compare X Layer swap routes, rank DEX options, decide whether execution should proceed, or turn quote data into a structured execution recommendation.
---

# X Layer Route Referee

Use this skill to evaluate one swap intent on X Layer and return the most reliable route recommendation.

The goal is not just to find the highest quoted output.
The goal is to judge route quality.

## When to use it

- The user wants to swap on X Layer and needs the best route.
- Another agent needs a reusable route-evaluation capability.
- The caller wants a quote plus route-quality explanation.
- The caller wants to compare Uniswap against other available venues.
- The caller wants a structured `execute / reduce-size / skip` decision.

## Required capabilities

Use `OnchainOS` as the factual layer:

- `DEX token` for token discovery and decimals
- `DEX liquidity` for available venues
- `DEX quote` for baseline and isolated route quotes
- optional wallet or swap layers only after a route recommendation is accepted

Do not invent tokens, quotes, price impact, or venues.

## Workflow

1. Extract:
   - `from token`
   - `to token`
   - `amount`
   - optional `slippage`
   - optional `preferred DEX list`
   - optional `banned DEX list`
2. Resolve both token addresses on X Layer.
3. Pull the available liquidity sources.
4. Get the baseline aggregated quote.
5. Get isolated quotes for the strongest venues.
6. Rank candidates on:
   - expected output
   - price impact
   - route concentration
   - fallback coverage
7. Return exactly one final verdict:
   - `execute`
   - `reduce-size`
   - `skip`
8. Explain the verdict with route evidence, not vague intuition.

## Fixed output

Always return these sections in this order:

1. `Swap intent`
2. `Best route`
3. `Alternative routes`
4. `Risk view`
5. `Verdict`
6. `Agent-ready summary`

## Output guidance

- Keep the answer structured.
- Do not hide tradeoffs when the best-output route is fragile.
- If impact is too high, prefer `reduce-size` over pretending the route is clean.
- If route quality is weak across the board, return `skip`.
- If Uniswap is present, state whether it won or lost and why.
