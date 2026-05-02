"""Finansportalen API client for fetching live mortgage rates."""

import httpx
from datetime import date

# Finansportalen open API for mortgage products
_API_URL = "https://www.finansportalen.no/api/bank/boliglan"

# Curated fallback rates (updated to reflect Norwegian market ~2025)
# These are used when the live API is unreachable
_FALLBACK_RATES = [
    {"bank": "Bulder Bank", "nominal_rate": 4.99, "effective_rate": 5.11},
    {"bank": "Landkreditt Bank", "nominal_rate": 5.09, "effective_rate": 5.22},
    {"bank": "Sbanken (DNB)", "nominal_rate": 5.14, "effective_rate": 5.27},
    {"bank": "Santander Consumer Bank", "nominal_rate": 5.19, "effective_rate": 5.32},
    {"bank": "SpareBank 1 SR-Bank", "nominal_rate": 5.24, "effective_rate": 5.37},
    {"bank": "Sparebanken Vest", "nominal_rate": 5.29, "effective_rate": 5.43},
    {"bank": "Handelsbanken", "nominal_rate": 5.29, "effective_rate": 5.43},
    {"bank": "Nordea", "nominal_rate": 5.34, "effective_rate": 5.48},
    {"bank": "DNB", "nominal_rate": 5.39, "effective_rate": 5.53},
    {"bank": "SpareBank 1 Østlandet", "nominal_rate": 5.24, "effective_rate": 5.38},
    {"bank": "Sparebanken Sør", "nominal_rate": 5.29, "effective_rate": 5.43},
    {"bank": "Sparebanken Møre", "nominal_rate": 5.34, "effective_rate": 5.48},
]


async def fetch_rates(loan_amount: int, ltv_percent: float) -> list[dict]:
    """
    Fetch current mortgage rates from Finansportalen.
    Falls back to curated data if the live API is unavailable.
    """
    live_rates = await _fetch_live_rates(loan_amount, ltv_percent)
    if live_rates:
        return live_rates

    today = date.today().isoformat()
    fallback = []
    for r in _FALLBACK_RATES:
        entry = r.copy()
        entry["date"] = today
        entry["source"] = "fallback"
        fallback.append(entry)
    return fallback


async def _fetch_live_rates(loan_amount: int, ltv_percent: float) -> list[dict] | None:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                _API_URL,
                params={"loanAmount": loan_amount, "ltv": ltv_percent},
                headers={"Accept": "application/json"},
            )
            if response.status_code == 200:
                data = response.json()
                parsed = _parse_response(data)
                if parsed:
                    return parsed
    except Exception:
        pass
    return None


def _parse_response(data) -> list[dict] | None:
    today = date.today().isoformat()
    items = data if isinstance(data, list) else data.get("products", data.get("results", []))
    rates = []
    for item in items:
        try:
            rate = {
                "bank": item.get("bankName", item.get("name", "Ukjent bank")),
                "nominal_rate": float(item.get("nominalRate", item.get("nominalInterestRate", 0))),
                "effective_rate": float(item.get("effectiveRate", item.get("effectiveInterestRate", 0))),
                "date": today,
                "source": "live",
            }
            if rate["nominal_rate"] > 0:
                rates.append(rate)
        except (KeyError, ValueError, TypeError):
            continue
    return rates or None
