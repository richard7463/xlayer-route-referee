# Live Validation

This project has already been validated against real OnchainOS quote endpoints on **April 10, 2026**.

## Environment

- network: `X Layer`
- chain index: `196`
- API base: `https://web3.okx.com`
- auth source: OKX Dev Portal project credentials
- proxy: local `7890`

## What Was Verified

1. `all-tokens` returned live token metadata
2. `get-liquidity` returned live venue metadata
3. `quote` returned real route results for:
   - `USDC -> OKB`
   - `USDC -> USDT`
4. a failure case was also captured honestly:
   - `USDC -> WBTC` returned `Insufficient liquidity`

## Observed Live Results

### USDC -> OKB

- verdict: `execute`
- route risk: `medium`
- best route: `Aggregated`
- best quoted output: `0.297907678843008126 OKB`
- strongest named alternatives:
  - `QuickSwap V3`
  - `Community AMM (V3)`

### USDC -> USDT

- verdict: `execute`
- route risk: `medium`
- best route: `Aggregated`
- best quoted output: `25.001436 USDT`
- strongest named alternatives:
  - `OkieStableSwap`
  - `CurveNG`
  - `Community AMM (V3)`

### USDC -> WBTC

- status: `error`
- honest result: `Insufficient liquidity`

## Proof Files

- [live-proof-latest.json](/Users/yanqing/Documents/GitHub/miraix-interface/projects/xlayer-route-referee/examples/live-proof-latest.json)

## Why This Matters

This means the project is no longer just a mock skill shell.
It now has:

- real token discovery
- real liquidity-source discovery
- real route comparisons
- an honest error path captured from live conditions
