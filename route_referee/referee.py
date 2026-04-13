from __future__ import annotations

import hashlib
from decimal import Decimal
from typing import Any, Dict, List

from .client import OnchainOSClient, OnchainOSError
from .models import RefereeCheck, RefereeDecision, RefereeRequest, RefereeResponse, RouteCandidate


class RouteReferee:
    def __init__(self, client: OnchainOSClient | None = None):
        self.client = client or OnchainOSClient()

    def evaluate(self, request: RefereeRequest) -> RefereeResponse:
        from_token = self.client.resolve_token(request.from_token)
        to_token = self.client.resolve_token(request.to_token)
        amount = self.client.to_base_units(request.amount, from_token.decimals)

        liquidity_sources = self.client.liquidity_sources()
        banned = {name.lower() for name in request.banned_dexes}
        preferred = [name for name in request.preferred_dexes if name.lower() not in banned]

        candidates: List[RouteCandidate] = []
        seen_ids: set[str] = set()

        baseline_quote = self.client.quote(
            amount=amount,
            from_token_address=from_token.address,
            to_token_address=to_token.address,
        )
        candidates.append(self._candidate_from_quote("Aggregated", "aggregated", baseline_quote, to_token.symbol, fallback_count=0))
        seen_ids.add("aggregated")

        ranked_sources = self._rank_source_names(liquidity_sources, preferred=preferred)
        source_ids = self.client.liquidity_id_map(ranked_sources)
        total_sources = max(len(source_ids), 1)

        for name in ranked_sources:
            if name.lower() in banned:
                continue
            dex_id = source_ids.get(name)
            if not dex_id or dex_id in seen_ids:
                continue
            try:
                quote = self.client.quote(
                    amount=amount,
                    from_token_address=from_token.address,
                    to_token_address=to_token.address,
                    dex_ids=dex_id,
                )
            except OnchainOSError:
                continue
            fallback_count = max(total_sources - 1, 0)
            candidates.append(self._candidate_from_quote(name, dex_id, quote, to_token.symbol, fallback_count=fallback_count))
            seen_ids.add(dex_id)
            if len(candidates) >= 6:
                break

        if not candidates:
            raise OnchainOSError("No route candidates available")

        candidates = sorted(candidates, key=self._sort_key, reverse=True)
        recommended = candidates[0]
        alternatives = candidates[1:4]
        checks = self._checks(request, recommended, alternatives)
        decision = self._decision(request, recommended, checks)
        verdict = decision.action
        route_risk = decision.risk_level
        proof_id = self._proof_id(request, recommended, checks, verdict)
        summary = self._summary(request, recommended, alternatives, decision)
        return RefereeResponse(
            request=request,
            verdict=verdict,
            route_risk=route_risk,
            recommended_route=recommended,
            alternative_routes=alternatives,
            checks=checks,
            decision=decision,
            proof_id=proof_id,
            agent_summary=summary,
        )

    @staticmethod
    def _rank_source_names(liquidity_sources: List[Dict[str, str]], *, preferred: List[str]) -> List[str]:
        names = [item["name"] for item in liquidity_sources if item.get("name")]
        preferred_lower = {name.lower() for name in preferred}
        preferred_names = [name for name in names if name.lower() in preferred_lower]
        remaining = [name for name in names if name.lower() not in preferred_lower]
        return preferred_names + remaining

    @staticmethod
    def _decimal(value: Any, default: str = "0") -> Decimal:
        raw = value if value not in (None, "") else default
        return Decimal(str(raw))

    def _candidate_from_quote(self, dex_name: str, dex_id: str, quote: Dict[str, Any], output_symbol: str, *, fallback_count: int) -> RouteCandidate:
        output_amount = self._decimal(quote.get("toTokenAmount"))
        output_decimals = int(quote.get("toToken", {}).get("decimal", quote.get("toTokenDecimal", 18)))
        normalized_output = self.client.from_base_units(str(output_amount), output_decimals)
        price_impact = self._decimal(quote.get("priceImpactPercentage", quote.get("priceImpact", "0")))
        route_concentration_score = self._route_concentration_score(price_impact=price_impact, fallback_count=fallback_count)
        verdict_hint = self._hint(route_concentration_score, price_impact)
        reason = self._reason(dex_name, normalized_output, price_impact, fallback_count)
        return RouteCandidate(
            dex_name=dex_name,
            dex_id=dex_id,
            output_amount=normalized_output,
            output_symbol=output_symbol,
            price_impact_percent=price_impact,
            route_concentration_score=route_concentration_score,
            fallback_count=fallback_count,
            verdict_hint=verdict_hint,
            reason=reason,
        )

    @staticmethod
    def _route_concentration_score(*, price_impact: Decimal, fallback_count: int) -> Decimal:
        concentration_penalty = Decimal("0.35") if fallback_count <= 0 else Decimal("0.12") / Decimal(str(fallback_count))
        impact_penalty = min(max(price_impact, Decimal("0")), Decimal("8")) / Decimal("10")
        raw = Decimal("1.00") - concentration_penalty - impact_penalty
        return max(raw, Decimal("0.05")).quantize(Decimal("0.01"))

    @staticmethod
    def _hint(route_concentration_score: Decimal, price_impact: Decimal) -> str:
        if price_impact > Decimal("2.00"):
            return "block"
        if price_impact > Decimal("1.20"):
            return "resize"
        if route_concentration_score < Decimal("0.45"):
            return "retry"
        return "execute"

    @staticmethod
    def _reason(dex_name: str, output_amount: Decimal, price_impact: Decimal, fallback_count: int) -> str:
        return (
            f"{dex_name} returns {output_amount.normalize()} output with {price_impact}% impact "
            f"and {fallback_count} fallback venues."
        )

    @staticmethod
    def _sort_key(candidate: RouteCandidate) -> tuple[Decimal, Decimal, int]:
        return (
            candidate.output_amount,
            candidate.route_concentration_score,
            candidate.fallback_count,
        )

    def _checks(self, request: RefereeRequest, recommended: RouteCandidate, alternatives: List[RouteCandidate]) -> List[RefereeCheck]:
        checks = [
            RefereeCheck(
                id="quote_available",
                ok=True,
                level="pass",
                note=f"recommended route={recommended.dex_name}",
            ),
            RefereeCheck(
                id="price_impact",
                ok=recommended.price_impact_percent <= request.max_price_impact_percent,
                level="pass" if recommended.price_impact_percent <= request.max_price_impact_percent else "warn",
                note=f"impact={recommended.price_impact_percent}% max={request.max_price_impact_percent}%",
            ),
            RefereeCheck(
                id="fallback_coverage",
                ok=recommended.fallback_count >= request.min_fallback_count or len(alternatives) >= request.min_fallback_count,
                level="pass" if recommended.fallback_count >= request.min_fallback_count or len(alternatives) >= request.min_fallback_count else "warn",
                note=f"candidate_fallbacks={recommended.fallback_count} alternatives={len(alternatives)} required={request.min_fallback_count}",
            ),
            RefereeCheck(
                id="banned_dex_exclusion",
                ok=recommended.dex_name.lower() not in {dex.lower() for dex in request.banned_dexes},
                level="pass",
                note=f"banned={','.join(request.banned_dexes) or 'none'}",
            ),
            RefereeCheck(
                id="agent_reason",
                ok=bool(request.reason.strip()),
                level="pass" if request.reason.strip() else "warn",
                note=request.reason.strip() or "missing reason",
            ),
        ]
        return checks

    @staticmethod
    def _risk_bucket(route_concentration_score: Decimal, price_impact: Decimal) -> str:
        if price_impact > Decimal("2.00"):
            return "critical"
        if price_impact > Decimal("1.20") or route_concentration_score < Decimal("0.45"):
            return "high"
        if price_impact > Decimal("0.60") or route_concentration_score < Decimal("0.70"):
            return "medium"
        return "low"

    def _decision(self, request: RefereeRequest, recommended: RouteCandidate, checks: List[RefereeCheck]) -> RefereeDecision:
        failed = [check.id for check in checks if not check.ok]
        risk_level = self._risk_bucket(recommended.route_concentration_score, recommended.price_impact_percent)
        if recommended.price_impact_percent > Decimal("2.00"):
            action = "block"
            size = Decimal("0")
        elif recommended.price_impact_percent > request.max_price_impact_percent:
            action = "resize"
            size = max(Decimal("0.10"), request.max_price_impact_percent / max(recommended.price_impact_percent, Decimal("0.01"))).quantize(Decimal("0.01"))
        elif "fallback_coverage" in failed:
            action = "retry"
            size = Decimal("1.00")
        else:
            action = recommended.verdict_hint
            size = Decimal("1.00") if action == "execute" else Decimal("0.50")

        rationale = (
            f"{action}: {recommended.dex_name} is the best current route for {request.agent_name} intent {request.intent_id}; "
            f"risk={risk_level}, impact={recommended.price_impact_percent}%, fallback_count={recommended.fallback_count}."
        )
        return RefereeDecision(
            action=action,
            risk_level=risk_level,
            recommended_size_multiplier=size,
            policy_hits=failed or ["route_within_referee_limits"],
            rationale=rationale,
        )

    @staticmethod
    def _proof_id(request: RefereeRequest, recommended: RouteCandidate, checks: List[RefereeCheck], verdict: str) -> str:
        material = "|".join(
            [
                request.agent_name,
                request.intent_id,
                request.from_token,
                request.to_token,
                str(request.amount),
                recommended.dex_name,
                str(recommended.output_amount),
                verdict,
                ",".join(f"{check.id}:{check.ok}" for check in checks),
            ]
        )
        return "route_referee_" + hashlib.sha256(material.encode()).hexdigest()[:16]

    @staticmethod
    def _summary(request: RefereeRequest, recommended: RouteCandidate, alternatives: List[RouteCandidate], decision: RefereeDecision) -> str:
        alt_names = ", ".join(candidate.dex_name for candidate in alternatives) if alternatives else "no viable fallback"
        return (
            f"Pre-execution verdict: {decision.action}. Agent={request.agent_name}, intent={request.intent_id}. "
            f"Prefer {recommended.dex_name}: {recommended.output_amount} {recommended.output_symbol}, "
            f"impact={recommended.price_impact_percent}%, risk={decision.risk_level}. "
            f"Alternatives checked: {alt_names}. {decision.rationale}"
        )
