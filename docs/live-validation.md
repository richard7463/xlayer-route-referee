# Live Validation

This project has been refreshed against real OnchainOS quote endpoints on **April 13, 2026**.

## Environment

- network: `X Layer`
- chain index: `196`
- API base: `https://web3.okx.com`
- auth source: OKX Dev Portal project credentials
- referee model: `pre_execution_route_referee`
- decision actions: `execute`, `resize`, `retry`, `block`

## What Was Verified

1. `all-tokens` returned live token metadata.
2. `get-liquidity` returned live venue metadata.
3. `quote` returned real route results for:
   - `USDC -> OKB`
   - `USDC -> USDT`
4. An honest failure case was captured:
   - `USDC -> WBTC` returned `Insufficient liquidity`.
5. The response now includes:
   - `proof_id`
   - `checks`
   - `decision`
   - `agent_summary`

## Observed Live Results

### USDC -> OKB

- verdict: `execute`
- route risk: `medium`
- best route: `Aggregated`
- proof ID: `route_referee_66ae6fe48c673a5f`
- decision rationale: execute under current route limits
- checks passed:
  - `quote_available`
  - `price_impact`
  - `fallback_coverage`
  - `banned_dex_exclusion`
  - `agent_reason`

### USDC -> USDT

- verdict: `execute`
- route risk: `low`
- best route: `CurveNG`
- proof ID: `route_referee_c6c38d0ef9b68647`
- checks passed:
  - `quote_available`
  - `price_impact`
  - `fallback_coverage`
  - `banned_dex_exclusion`
  - `agent_reason`

### USDC -> WBTC

- status: `error`
- honest result: `OKX API error 82000: Insufficient liquidity`

## Proof Files

- [live-proof-latest.json](/Users/yanqing/Documents/GitHub/miraix-interface/projects/xlayer-route-referee/examples/live-proof-latest.json)
- [live-proof-2026-04-13.json](/Users/yanqing/Documents/GitHub/miraix-interface/projects/xlayer-route-referee/examples/live-proof-2026-04-13.json)

## Why This Matters

This means the project is no longer a thin quote wrapper.
It has:

- real token discovery
- real liquidity-source discovery
- real route comparisons
- a pre-execution decision model
- an honest error path captured from live conditions
