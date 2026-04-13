from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from route_referee.client import OnchainOSClient, OnchainOSError
from route_referee.models import RefereeRequest
from route_referee.referee import RouteReferee

ENV_PATH = ROOT / ".env"
OUTPUT_DIR = ROOT / "examples"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        if "=" not in line or line.strip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value)


def default_proxy() -> None:
    proxy = (
        os.getenv("ONCHAINOS_PROXY")
        or os.getenv("OKX_AGENT_PROXY")
        or os.getenv("MOLTBOOK_PROXY")
        or os.getenv("HTTPS_PROXY")
        or os.getenv("HTTP_PROXY")
    )
    if proxy and not os.getenv("ONCHAINOS_PROXY"):
        os.environ["ONCHAINOS_PROXY"] = proxy


def decimal_to_str(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, list):
        return [decimal_to_str(item) for item in value]
    if isinstance(value, dict):
        return {key: decimal_to_str(item) for key, item in value.items()}
    return value


def main() -> None:
    load_env(ENV_PATH)
    default_proxy()

    client = OnchainOSClient()
    referee = RouteReferee(client=client)

    pairs = [
        ("USDC", "OKB", Decimal("25")),
        ("USDC", "USDT", Decimal("25")),
        ("USDC", "WBTC", Decimal("25")),
    ]

    evaluations: List[Dict[str, Any]] = []
    for from_token, to_token, amount in pairs:
        try:
            response = referee.evaluate(
                RefereeRequest(
                    from_token=from_token,
                    to_token=to_token,
                    amount=amount,
                    preferred_dexes=["Uniswap V3"],
                    agent_name="route-referee-demo-agent",
                    intent_id=f"live-{from_token.lower()}-{to_token.lower()}",
                    reason="pre-execution route quality check for an autonomous X Layer agent",
                    max_price_impact_percent=Decimal("1.20"),
                    min_fallback_count=1,
                )
            )
            evaluations.append(
                {
                    "pair": f"{from_token}->{to_token}",
                    "status": "success",
                    "response": decimal_to_str(asdict(response)),
                }
            )
        except OnchainOSError as exc:
            evaluations.append(
                {
                    "pair": f"{from_token}->{to_token}",
                    "status": "error",
                    "error": str(exc),
                }
            )

    captured_at = datetime.now(timezone.utc)
    dated_output_path = OUTPUT_DIR / f"live-proof-{captured_at.date().isoformat()}.json"
    latest_output_path = OUTPUT_DIR / "live-proof-latest.json"

    payload = {
        "captured_at_utc": captured_at.isoformat(),
        "referee_model": "pre_execution_route_referee",
        "decision_actions": ["execute", "resize", "retry", "block"],
        "chain_index": client.chain_index,
        "api_base": client.base_url,
        "token_count": len(client.supported_tokens()),
        "liquidity_sources": client.liquidity_sources(),
        "evaluations": evaluations,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2)
    dated_output_path.write_text(rendered)
    latest_output_path.write_text(rendered)
    print(dated_output_path)


if __name__ == "__main__":
    main()
