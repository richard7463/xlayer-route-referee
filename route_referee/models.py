from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List


@dataclass(frozen=True)
class TokenRef:
    symbol: str
    address: str
    decimals: int


@dataclass(frozen=True)
class RefereeRequest:
    from_token: str
    to_token: str
    amount: Decimal
    slippage_percent: Decimal = Decimal("0.5")
    preferred_dexes: List[str] = field(default_factory=list)
    banned_dexes: List[str] = field(default_factory=list)
    agent_name: str = "unknown-agent"
    intent_id: str = "manual-intent"
    reason: str = "agent requested route preflight"
    max_price_impact_percent: Decimal = Decimal("1.20")
    min_fallback_count: int = 1


@dataclass(frozen=True)
class RouteCandidate:
    dex_name: str
    dex_id: str
    output_amount: Decimal
    output_symbol: str
    price_impact_percent: Decimal
    route_concentration_score: Decimal
    fallback_count: int
    verdict_hint: str
    reason: str


@dataclass(frozen=True)
class RefereeCheck:
    id: str
    ok: bool
    level: str
    note: str


@dataclass(frozen=True)
class RefereeDecision:
    action: str
    risk_level: str
    recommended_size_multiplier: Decimal
    policy_hits: List[str]
    rationale: str


@dataclass(frozen=True)
class RefereeResponse:
    request: RefereeRequest
    verdict: str
    route_risk: str
    recommended_route: RouteCandidate
    alternative_routes: List[RouteCandidate]
    checks: List[RefereeCheck]
    decision: RefereeDecision
    proof_id: str
    agent_summary: str
