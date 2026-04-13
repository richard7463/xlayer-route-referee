---
name: xlayer-route-referee
description: Use this skill when an agent needs a pre-execution verdict for an X Layer swap intent: compare routes, assess price impact and fallback coverage, exclude banned venues, and return execute / resize / retry / block with proof.
---

# X Layer Route Referee

Use this skill to evaluate one swap intent on X Layer before execution.

The goal is not just to find the highest quoted output.
The goal is to judge whether the route is safe enough for an autonomous agent to execute.

## When to use it

- An agent is about to swap on X Layer.
- A trading bot needs to decide whether to execute, resize, retry, or block.
- A treasury agent needs route evidence before rebalancing.
- A payment agent needs to avoid fragile or banned venues.
- A caller wants Uniswap compared against other available X Layer liquidity venues.
- A caller wants a Moltbook-ready execution explanation.

## Required factual layer

Use OnchainOS as the factual layer:

- token discovery for token addresses and decimals
- liquidity-source discovery for available venues
- quote retrieval for baseline and isolated route quotes
- optional wallet or swap execution only after the route referee returns an acceptable verdict

Do not invent tokens, quotes, price impact, route names, or liquidity venues.

## Input fields

Extract or ask for:

- `agent_name`
- `intent_id`
- `from_token`
- `to_token`
- `amount`
- optional `slippage_percent`
- optional `preferred_dexes`
- optional `banned_dexes`
- optional `reason`
- optional `max_price_impact_percent`
- optional `min_fallback_count`

## Workflow

1. Resolve both token addresses on X Layer.
2. Pull available liquidity sources.
3. Get the baseline aggregated quote.
4. Get isolated quotes for major venues, especially preferred venues such as Uniswap.
5. Rank candidates by output, price impact, route concentration, and fallback coverage.
6. Run checks:
   - `quote_available`
   - `price_impact`
   - `fallback_coverage`
   - `banned_dex_exclusion`
   - `agent_reason`
7. Return one final verdict:
   - `execute`
   - `resize`
   - `retry`
   - `block`
8. Include a proof ID and agent-ready summary.

## Fixed output

Always return these sections in this order:

1. `Agent trade intent`
2. `Recommended route`
3. `Alternative routes`
4. `Referee checks`
5. `Decision`
6. `Proof ID`
7. `Agent-ready summary`

## Decision guidance

- Use `execute` only when quote, impact, fallback, and policy checks are acceptable.
- Use `resize` when route exists but size is too aggressive for impact constraints.
- Use `retry` when the route is available but fragile or insufficiently covered by fallbacks.
- Use `block` when impact or policy failure makes execution unacceptable.
- If Uniswap is present, state whether it won or lost and why.
