"""Fetch county-level Fair Market Rents from the HUD User API.

Requires a free API token from https://www.huduser.gov/hudapi/. Set the
token in the environment as ``HUD_API_TOKEN`` before running.

Usage:
    python -m policyengine_us.tools.download_hud_fmr \
        --year 2025 \
        --output policyengine_us/parameters/gov/hud/fmr/fair_market_rents.csv

The output CSV matches the schema documented in
``policyengine_us/parameters/gov/hud/fmr/README.md``. Re-running for a new
year appends rather than overwriting; the script de-duplicates on
``(state, county_fips, year, bedrooms)``.
"""

import argparse
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

API_ROOT = "https://www.huduser.gov/hudapi/public/fmr"

# Bedroom keys in the HUD API response, mapped to integer counts.
BEDROOM_FIELDS = {
    0: "Efficiency",
    1: "One-Bedroom",
    2: "Two-Bedroom",
    3: "Three-Bedroom",
    4: "Four-Bedroom",
}


def get(url: str, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    return response.json()


def list_states(token: str) -> list[str]:
    data = get(f"{API_ROOT}/listStates", token)
    return [row["state_code"] for row in data]


def state_rows(state_code: str, year: int, token: str) -> pd.DataFrame:
    """Return one row per (county_fips, bedrooms) for the state and year."""
    payload = get(f"{API_ROOT}/data/{state_code}?year={year}", token)
    rows = []
    for county in payload.get("data", {}).get("counties", []):
        fips = str(county.get("fips_code", "")).zfill(5)
        for bedrooms, key in BEDROOM_FIELDS.items():
            value = county.get(key)
            if value is None:
                continue
            rows.append(
                {
                    "state": state_code,
                    "county_fips": fips,
                    "year": year,
                    "bedrooms": bedrooms,
                    "value": float(value),
                }
            )
    return pd.DataFrame(rows)


def fetch_year(year: int, token: str) -> pd.DataFrame:
    frames = []
    for state in list_states(token):
        try:
            frames.append(state_rows(state, year, token))
        except requests.HTTPError as err:
            print(f"  {state}: skipped ({err})", file=sys.stderr)
        time.sleep(0.1)  # polite rate-limit
    return pd.concat(frames, ignore_index=True)


def merge_with_existing(new: pd.DataFrame, output: Path) -> pd.DataFrame:
    if not output.exists():
        return new
    existing = pd.read_csv(output, dtype={"county_fips": str})
    combined = pd.concat([existing, new], ignore_index=True)
    return combined.drop_duplicates(
        subset=["state", "county_fips", "year", "bedrooms"], keep="last"
    ).sort_values(["state", "county_fips", "year", "bedrooms"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    token = os.environ.get("HUD_API_TOKEN")
    if not token:
        print(
            "ERROR: set HUD_API_TOKEN (register at https://www.huduser.gov/hudapi/)",
            file=sys.stderr,
        )
        return 2

    fetched = fetch_year(args.year, token)
    combined = merge_with_existing(fetched, args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(args.output, index=False)
    print(f"Wrote {len(combined):,} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
