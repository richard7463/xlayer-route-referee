from decimal import Decimal

from route_referee.client import TokenInfo
from route_referee.models import RefereeRequest
from route_referee.referee import RouteReferee


class FakeClient:
    def __init__(self):
        self.chain_index = "196"
        self._sources = [
            {"id": "1", "name": "Uniswap V3"},
            {"id": "2", "name": "Oku"},
            {"id": "3", "name": "PangeaSwap"},
        ]

    def resolve_token(self, symbol):
        if symbol == "USDC":
            return TokenInfo(symbol="USDC", address="0xusdc", decimals=6)
        return TokenInfo(symbol="OKB", address="0xokb", decimals=18)

    def to_base_units(self, amount, decimals):
        return str(int(amount * (Decimal(10) ** decimals)))

    def from_base_units(self, amount, decimals):
        return Decimal(str(amount)) / (Decimal(10) ** decimals)

    def liquidity_sources(self):
        return self._sources

    def liquidity_id_map(self, names):
        return {item["name"]: item["id"] for item in self._sources if item["name"] in names}

    def quote(self, *, amount, from_token_address, to_token_address, dex_ids=None):
        quotes = {
            None: {"toTokenAmount": "104000000000000000000", "toToken": {"decimal": 18}, "priceImpactPercentage": "0.35"},
            "1": {"toTokenAmount": "104300000000000000000", "toToken": {"decimal": 18}, "priceImpactPercentage": "0.40"},
            "2": {"toTokenAmount": "103900000000000000000", "toToken": {"decimal": 18}, "priceImpactPercentage": "0.31"},
            "3": {"toTokenAmount": "103600000000000000000", "toToken": {"decimal": 18}, "priceImpactPercentage": "0.82"},
        }
        return quotes[dex_ids]


def test_prefers_best_route_with_clean_impact():
    referee = RouteReferee(client=FakeClient())
    request = RefereeRequest(from_token="USDC", to_token="OKB", amount=Decimal("25"), preferred_dexes=["Uniswap V3"])
    response = referee.evaluate(request)
    assert response.recommended_route.dex_name == "Uniswap V3"
    assert response.verdict == "execute"
    assert response.route_risk in {"low", "medium"}
