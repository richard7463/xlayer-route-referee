# X Post

```text
Built X Layer Route Referee for the OKX Build X Hackathon Skills Arena.

It is a reusable pre-execution referee for autonomous X Layer agents.

Agent trade intent -> live OnchainOS quotes -> route risk checks -> execute / resize / retry / block.

Latest live validation:
- USDC -> OKB: execute, medium risk
- USDC -> USDT: execute, low risk
- USDC -> WBTC: honest insufficient-liquidity failure captured

This is not a trading bot.
It is the judgment layer agents call before they trade.

Repo:
https://github.com/richard7463/xlayer-route-referee

Proof:
https://github.com/richard7463/xlayer-route-referee/blob/main/examples/live-proof-latest.json

#BuildX #onchainos @XLayerOfficial
```
