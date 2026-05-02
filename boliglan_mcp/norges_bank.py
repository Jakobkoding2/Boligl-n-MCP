"""Norges Bank API client for policy rate and forecast (rentebane)."""

import httpx

# SDMX-JSON API – key policy rate (styringsrenten)
_IR_URL = "https://data.norges-bank.no/api/data/IR/B.KPRA.SD.NOK"

# Monetary Policy Report – forward rate path
_MPR_URL = "https://data.norges-bank.no/api/data/MPR/Q.FOLIO.FW_Q"

# Fallback values reflecting Norges Bank's published expectations (~2025)
_FALLBACK_POLICY_RATE = 4.50
_FALLBACK_FORECAST = {
    "2025-Q1": 4.50,
    "2025-Q2": 4.25,
    "2025-Q3": 4.00,
    "2025-Q4": 3.75,
    "2026-Q1": 3.50,
    "2026-Q2": 3.25,
    "2027-Q1": 3.00,
}


async def fetch_policy_rate() -> float:
    """Return the current Norges Bank policy rate (styringsrenten)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                _IR_URL,
                params={"format": "sdmx-json", "lastNObservations": 1, "locale": "no"},
            )
            if resp.status_code == 200:
                data = resp.json()
                series = data["data"]["dataSets"][0]["series"]
                for val in series.values():
                    obs = val["observations"]
                    if obs:
                        latest = obs[max(obs, key=int)]
                        return float(latest[0])
    except Exception:
        pass
    return _FALLBACK_POLICY_RATE


async def fetch_rate_forecast() -> dict[str, float]:
    """Return Norges Bank's policy rate forecast (rentebane) by quarter."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                _MPR_URL,
                params={"format": "sdmx-json", "locale": "no"},
            )
            if resp.status_code == 200:
                data = resp.json()
                parsed = _parse_forecast(data)
                if parsed:
                    return parsed
    except Exception:
        pass
    return _FALLBACK_FORECAST.copy()


def _parse_forecast(data: dict) -> dict[str, float] | None:
    try:
        time_periods = data["data"]["structure"]["dimensions"]["observation"][0]["values"]
        series = data["data"]["dataSets"][0]["series"]
        forecast = {}
        for val in series.values():
            for idx_str, obs_vals in val["observations"].items():
                if obs_vals[0] is not None:
                    period = time_periods[int(idx_str)]["id"]
                    forecast[period] = float(obs_vals[0])
        return forecast or None
    except (KeyError, IndexError, TypeError):
        return None
