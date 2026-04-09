from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from decimal import Decimal

from .models import RefereeRequest
from .referee import RouteReferee


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
