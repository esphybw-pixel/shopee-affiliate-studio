from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


@dataclass(frozen=True)
class ProductScore:
    total: int
    commission: int
    demand: int
    visual_proof: int
    impulse: int
    trust: int
    risk: int
    verdict: str

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def score_product(product: dict[str, Any]) -> ProductScore:
    """Transparent heuristic. Gemini may explain the score but cannot invent its inputs."""
    price = _number(product.get("price"))
    commission_value = _number(product.get("commission"))
    commission_rate = (commission_value / price * 100) if price else 0
    sales_text = str(product.get("sales", "")).replace(",", "")
    digits = "".join(ch for ch in sales_text if ch.isdigit() or ch == ".")
    sales = _number(digits)
    notes = str(product.get("notes", "")).strip()
    image_url = str(product.get("image_url", "")).strip()

    commission = min(100, round(commission_rate * 6 + min(commission_value, 40)))
    demand = min(100, round(20 + (sales ** 0.5) * 1.5)) if sales else 35
    visual_proof = 78 if image_url and notes else 58 if image_url or notes else 35
    impulse = 88 if 79 <= price <= 399 else 72 if 40 <= price <= 699 else 52
    trust = min(88, 50 + (18 if sales >= 100 else 0) + (12 if notes else 0))
    risk = 18 if notes else 35
    total = round(
        commission * 0.22
        + demand * 0.20
        + visual_proof * 0.22
        + impulse * 0.16
        + trust * 0.20
        - risk * 0.08
    )
    total = max(0, min(100, total))
    verdict = "ผลิตทันที" if total >= 80 else "ทดสอบก่อน" if total >= 62 else "ยังไม่แนะนำ"
    return ProductScore(total, commission, demand, visual_proof, impulse, trust, risk, verdict)


def content_pack(product: dict[str, Any], analysis: dict[str, Any], character: str, mode: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "product": product,
        "score": score_product(product).as_dict(),
        "character": character,
        "mode": mode,
        "analysis": analysis,
        "production": {
            "aspect_ratio": "9:16",
            "resolution": "1080x1920",
            "target_duration_seconds": 18,
            "safe_claims_only": True,
            "video_status": "draft",
        },
    }


def flow_package_text(pack: dict[str, Any]) -> str:
    analysis = pack.get("analysis", {})
    product = pack.get("product", {})
    return "\n".join(
        [
            "VERTICAL SOCIAL COMMERCE VIDEO — 9:16",
            f"Product: {product.get('name', 'Unknown product')}",
            f"Character: {pack.get('character', 'No character')}",
            f"Format: {pack.get('mode', 'Problem to Demo')}",
            f"Hook: {analysis.get('hook', '')}",
            "Preserve the exact product shape, packaging, color and logo from the reference image.",
            "Do not invent prices, discounts, reviews, medical claims or product capabilities.",
            "Natural Thai social-commerce pacing, realistic movement, clean lighting, product clearly visible.",
            "Generate short scenes of 3–6 seconds so damaged scenes can be regenerated independently.",
            "Storyboard:",
            json.dumps(analysis.get("scenes", []), ensure_ascii=False, indent=2),
        ]
    )


def quality_report(pack: dict[str, Any]) -> dict[str, Any]:
    analysis = pack.get("analysis", {})
    product = pack.get("product", {})
    checks = {
        "product_data": 100 if product.get("name") and product.get("url") else 45,
        "hook": 92 if len(str(analysis.get("hook", ""))) >= 12 else 50,
        "storyboard": 92 if len(analysis.get("scenes", [])) >= 3 else 55,
        "caption": 90 if analysis.get("caption") else 40,
        "affiliate_link": 100 if product.get("url") else 0,
        "claim_safety": 96 if analysis.get("risks") is not None else 65,
    }
    total = round(sum(checks.values()) / len(checks))
    return {"score": total, "passed": total >= 88 and min(checks.values()) >= 80, "checks": checks}
