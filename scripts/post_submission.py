from __future__ import annotations

import os
import re
from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
POST_PATH = ROOT / "docs" / "submission-post.md"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        if "=" not in line or line.strip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value)


def extract_submission_post(path: Path) -> tuple[str, str]:
    text = path.read_text()
    title_match = re.search(r"Title:\s*\n\s*`([^`]+)`", text)
    body_match = re.search(r"Body:\s*\n\s*```md\n(.*?)\n```", text, re.S)
    if not title_match or not body_match:
        raise RuntimeError("Unable to parse submission post template.")
    return title_match.group(1).strip(), body_match.group(1).strip()


@dataclass
class MoltbookClient:
    api_key: str
    base_url: str
    submolt: str
    timeout: int
    proxies: Optional[Dict[str, str]]

    @classmethod
    def from_env(cls) -> "MoltbookClient":
        proxy = os.getenv("MOLTBOOK_PROXY", "").strip()
        return cls(
            api_key=os.getenv("MOLTBOOK_API_KEY", ""),
            base_url=os.getenv("MOLTBOOK_API_BASE", "https://www.moltbook.com/api/v1").rstrip("/"),
            submolt=os.getenv("MOLTBOOK_SUBMOLT", "buildx"),
            timeout=int(os.getenv("MOLTBOOK_TIMEOUT", "20")),
            proxies={"http": proxy, "https": proxy} if proxy else None,
        )

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "route-referee-moltbook/1.0",
        }

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        return requests.request(
            method=method,
            url=f"{self.base_url}{path}",
            timeout=self.timeout,
            proxies=self.proxies,
            **kwargs,
        )

    def check_claim_status(self) -> Dict[str, Any]:
        resp = self._request("GET", "/agents/status", headers=self._headers())
        body = resp.json() if "application/json" in resp.headers.get("content-type", "") else {"raw": resp.text}
        return {"status_code": resp.status_code, "body": body}

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"[^a-z0-9\\s]", " ", text.lower())

    def _extract_numbers(self, challenge: str) -> List[float]:
        nums: List[float] = []
        for m in re.findall(r"-?\\d+(?:\\.\\d+)?", challenge):
            nums.append(float(m))

        units = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
            "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
            "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
            "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
        }
        words = self._normalize_text(challenge).split()
        dictionary = list(units.keys())
        i = 0
        while i < len(words):
            word = words[i]
            if word not in units:
                match = get_close_matches(word, dictionary, n=1, cutoff=0.86)
                if match:
                    word = match[0]
            if word in units:
                value = units[word]
                if value >= 20 and i + 1 < len(words) and words[i + 1] in units and units[words[i + 1]] < 10:
                    value += units[words[i + 1]]
                    i += 1
                nums.append(float(value))
            i += 1
        return nums

    def _detect_op(self, challenge: str) -> Optional[str]:
        txt = self._normalize_text(challenge)
        if any(key in txt for key in ["total", "sum", "combined", "together", "plus", "add", "gains", "speeds up by", "increase by"]):
            return "+"
        if any(key in txt for key in ["minus", "subtract", "less by", "slows by", "decrease by", "drops by"]):
            return "-"
        if any(key in txt for key in ["times", "multiplied by"]):
            return "*"
        if any(key in txt for key in ["divided by", "divide by"]):
            return "/"
        symbols = re.findall(r"[+\\-*/]", challenge)
        return symbols[0] if symbols else None

    def _solve_challenge(self, challenge: str) -> str:
        numbers = self._extract_numbers(challenge)
        op = self._detect_op(challenge)
        if len(numbers) < 2 or op is None:
            raise RuntimeError(f"Unable to solve challenge: {challenge}")
        a, b = numbers[0], numbers[1]
        if op == "+":
            value = a + b
        elif op == "-":
            value = a - b
        elif op == "*":
            value = a * b
        else:
            value = a / b
        return f"{value:.2f}"

    def _verify_if_needed(self, body: Dict[str, Any]) -> Dict[str, Any]:
        verification = body.get("post", {}).get("verification")
        if not verification:
            return {"success": True, "verified": False, "reason": "no_verification_required"}
        payload = {
            "verification_code": verification["verification_code"],
            "answer": self._solve_challenge(verification["challenge_text"]),
        }
        resp = self._request("POST", "/verify", headers=self._headers(), json=payload)
        verify_body = resp.json() if "application/json" in resp.headers.get("content-type", "") else {"raw": resp.text}
        return {"success": resp.status_code in (200, 201), "verified": resp.status_code in (200, 201), "response": verify_body}

    def create_post(self, title: str, content: str) -> Dict[str, Any]:
        claim = self.check_claim_status()
        claim_body = claim.get("body", {})
        if claim.get("status_code") != 200 or claim_body.get("status") != "claimed":
            return {"success": False, "error": "agent not claimed", "claim": claim}
        payload = {
            "submolt_name": self.submolt,
            "title": title[:300],
            "content": content[:40000],
            "type": "text",
        }
        resp = self._request("POST", "/posts", headers=self._headers(), json=payload)
        body = resp.json() if "application/json" in resp.headers.get("content-type", "") else {"raw": resp.text}
        if resp.status_code not in (200, 201):
            return {"success": False, "status_code": resp.status_code, "response": body}
        return {"success": True, "status_code": resp.status_code, "response": body, "verification": self._verify_if_needed(body)}


def main() -> int:
    load_env(ENV_PATH)
    client = MoltbookClient.from_env()
    title, content = extract_submission_post(POST_PATH)
    result = client.create_post(title, content)
    print(result)
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
