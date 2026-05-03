from __future__ import annotations

from typing import Any

from policyengine_core.periods import instant

from policyengine_us.parameters.uprating_extensions import (
    extend_social_security_payroll_cap,
)


TRUSTEES_2025_NAWI_ASSUMPTION: dict[str, Any] = {
    "name": "trustees-2025-nawi-v1",
    "description": (
        "SSA 2025 Trustees intermediate projection for the National Average "
        "Wage Index, used by explicit long-run Trustees scenarios."
    ),
    "source": "SSA 2025 Trustees Report table V.B1",
    "start_year": 2034,
    "end_year": 2100,
    "not_default_current_law": True,
}

# SSA 2025 Trustees Report, table V.B1, intermediate assumptions. Values are
# annual percentage changes in the nominal average annual wage in covered
# employment for the listed calendar year.
TRUSTEES_2025_AVERAGE_WAGE_GROWTH_PCT: dict[int, float] = {
    2034: 3.85,
    2035: 3.72,
    2036: 3.65,
    2037: 3.66,
    2038: 3.66,
    2039: 3.68,
    2040: 3.65,
    2041: 3.63,
    2042: 3.62,
    2043: 3.60,
    2044: 3.57,
    2045: 3.55,
    2046: 3.53,
    2047: 3.53,
    2048: 3.53,
    2049: 3.52,
    2050: 3.51,
    2051: 3.51,
    2052: 3.51,
    2053: 3.50,
    2054: 3.50,
    2055: 3.49,
    2056: 3.50,
    2057: 3.51,
    2058: 3.52,
    2059: 3.52,
    2060: 3.53,
    2061: 3.53,
    2062: 3.54,
    2063: 3.55,
    2064: 3.55,
    2065: 3.55,
    2066: 3.55,
    2067: 3.56,
    2068: 3.55,
    2069: 3.55,
    2070: 3.56,
    2071: 3.55,
    2072: 3.55,
    2073: 3.55,
    2074: 3.55,
    2075: 3.56,
    2076: 3.56,
    2077: 3.56,
    2078: 3.56,
    2079: 3.56,
    2080: 3.55,
    2081: 3.56,
    2082: 3.56,
    2083: 3.56,
    2084: 3.56,
    2085: 3.56,
    2086: 3.57,
    2087: 3.56,
    2088: 3.56,
    2089: 3.56,
    2090: 3.56,
    2091: 3.56,
    2092: 3.56,
    2093: 3.55,
    2094: 3.55,
    2095: 3.55,
    2096: 3.55,
    2097: 3.55,
    2098: 3.55,
    2099: 3.55,
    2100: 3.55,
}


def apply_trustees_2025_nawi_projection(
    parameters,
    *,
    start_year: int = 2034,
    end_year: int = 2100,
) -> None:
    nawi = parameters.gov.ssa.nawi
    previous_value = float(nawi(f"{start_year - 1}-01-01"))
    values_by_year = {}

    for year in range(start_year, end_year + 1):
        try:
            growth = 1 + TRUSTEES_2025_AVERAGE_WAGE_GROWTH_PCT[year] / 100
        except KeyError as error:
            raise ValueError(
                f"No SSA Trustees 2025 NAWI growth rate for {year}."
            ) from error
        previous_value *= growth
        values_by_year[year] = previous_value

    for year, value in values_by_year.items():
        nawi.update(period=f"year:{year}-01-01:1", value=value)

    if values_by_year:
        nawi.update(
            start=instant(f"{end_year}-01-01"),
            value=values_by_year[end_year],
        )


def apply_trustees_2025_economic_assumptions(
    parameters,
    *,
    end_year: int = 2100,
) -> None:
    apply_trustees_2025_nawi_projection(parameters, end_year=end_year)
    extend_social_security_payroll_cap(
        parameters,
        last_projected_year=2035,
        end_year=end_year,
    )
