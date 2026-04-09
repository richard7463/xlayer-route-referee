from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from .client import OnchainOSClient, OnchainOSError
from .models import RefereeRequest, RefereeResponse, RouteCandidate


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
        verdict = self._final_verdict(recommended)
        route_risk = self._risk_bucket(recommended.route_concentration_score, recommended.price_impact_percent)
        summary = self._summary(recommended, alternatives, verdict)
        return RefereeResponse(
            request=request,
            verdict=verdict,
            route_risk=route_risk,
            recommended_route=recommended,
            alternative_routes=alternatives,
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
        if price_impact > Decimal("1.20"):
            return "reduce-size"
        if route_concentration_score < Decimal("0.45"):
            return "skip"
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

    @staticmethod
    def _risk_bucket(route_concentration_score: Decimal, price_impact: Decimal) -> str:
        if price_impact > Decimal("1.20") or route_concentration_score < Decimal("0.45"):
            return "high"
        if price_impact > Decimal("0.60") or route_concentration_score < Decimal("0.70"):
            return "medium"
        return "low"

    @staticmethod
    def _final_verdict(candidate: RouteCandidate) -> str:
        return candidate.verdict_hint

    @staticmethod
    def _summary(recommended: RouteCandidate, alternatives: List[RouteCandidate], verdict: str) -> str:
        alt_names = ", ".join(candidate.dex_name for candidate in alternatives) if alternatives else "no viable fallback"
        return (
            f"Verdict: {verdict}. Prefer {recommended.dex_name} because it offers {recommended.output_amount} "
            f"{recommended.output_symbol} with {recommended.price_impact_percent}% impact. "
            f"Alternatives checked: {alt_names}."
        )
