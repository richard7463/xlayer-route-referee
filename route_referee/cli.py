from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

from .models import RefereeRequest
from .referee import RouteReferee


ROOT = Path(__file__).resolve().parents[1]


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="X Layer Route Referee CLI")
    parser.add_argument("--from-token", required=True)
    parser.add_argument("--to-token", required=True)
    parser.add_argument("--amount", required=True)
    parser.add_argument("--slippage", default="0.5")
    parser.add_argument("--prefer-dex", action="append", default=[])
    parser.add_argument("--ban-dex", action="append", default=[])
    return parser.parse_args()


def main() -> None:
    load_env(ROOT / ".env")
    default_proxy()
    args = parse_args()
    request = RefereeRequest(
        from_token=args.from_token,
        to_token=args.to_token,
        amount=Decimal(args.amount),
        slippage_percent=Decimal(args.slippage),
        preferred_dexes=args.prefer_dex,
        banned_dexes=args.ban_dex,
    )
    referee = RouteReferee()
    response = referee.evaluate(request)
    print(json.dumps(asdict(response), indent=2, default=str))


if __name__ == "__main__":
    main()
