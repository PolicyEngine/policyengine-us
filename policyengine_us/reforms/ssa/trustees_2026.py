"""The 2026 Social Security Trustees' intermediate wage and price paths.

Long-range scoring has to match the Trustees' taxable payroll. By default
PolicyEngine-US loads CBO's February 2026 projections of the national average
wage index (``gov.ssa.nawi``) and of the index that uprates benefits
(``gov.ssa.uprating``), then extends each at its last projected growth. The
taxable maximum, the PIA bend points and the other wage-indexed amounts all
run on ``gov.ssa.nawi``. This module puts both paths on the intermediate
assumptions of the 2026 OASDI Trustees Report. It moves prices with wages, so
real wage growth matches the Trustees' path rather than the CBO extension's.
It is an explicit scenario assumption and stays off by default: current-law
output doesn't change unless a caller applies it.

Source: The 2026 Annual Report of the Board of Trustees of the Federal
Old-Age and Survivors Insurance and Federal Disability Insurance Trust Funds,
single-year tables, Table VI.G1, intermediate assumptions, columns "Adjusted
CPI" (2026 = 100) and "AWI", 2025 to 2100
(https://www.ssa.gov/oact/TR/2026/SingleYearTRTables_TR2026.xlsx, workbook
sha256 38d8c5fee2f8b46dc15dd689c82a080163d190f260066f7e34bbc51f2d6ba361).

Chain rule. The module chains the Trustees' growth onto published values; it
never writes the Trustees' levels.

- ``gov.ssa.nawi``: NAWI(2025) stays the published 72,800.33. For each later
  year Y, NAWI(Y) = NAWI(Y - 1) * AWI(Y) / AWI(Y - 1).
- ``gov.ssa.uprating``: the value at Y-01-01 holds the third-quarter CPI-W of
  Y - 1, and 2027-01-01 (the 2026 third quarter, 328.746) is the last actual.
  For each Y from 2028, U(Y) = U(Y - 1) * ACPI(Y - 1) / ACPI(Y - 2).

Both paths hold their ``end_year`` value after ``end_year``.

Reach. From those two paths the module re-derives:

- the SOI income totals that age microdata incomes, from 2037, with
  ``apply_trustees_2025_soi_income_projection``, when ``end_year`` is after
  2036;
- the contribution and benefit base from 2028, since SSA last determined it
  for 2027 and the 2028 to 2036 values in its YAML derive from CBO;
- the base's owners' draw copy, ``gov.contrib.ssa.owners_draw.current_law_cap``,
  on the same rule from the copy's own values through 2027, so a policy reform
  that changes the live base doesn't reach it;
- the wage base, quarter-of-coverage threshold, earnings-test exempt amounts,
  PIA bend points and SGA amounts, from 2027;
- every parameter whose ``uprating`` metadata names either path. Core's
  ``uprate_parameters`` writes their values when the system builds, so a later
  change to a path doesn't reach them. The module derives each again as core
  would from the new path: its last value stated in YAML times the path's
  ratio, with the parameter's own rounding, for every year after the path's
  last unchanged year (2025 for NAWI, 2027 for the uprating index). It raises
  for a reader that states a value after that year or uprates on a cadence.

Limits. Table VI.G1 labels the price series "Adjusted CPI" and Table V.B1
labels it "Consumer Price Index"; neither names the CPI-W. The module treats
it as the path behind benefit COLAs. Other price paths keep their CBO
extensions: CPI-U, chained CPI-U, ``gov.irs.uprating``, and the SNAP and HHS
upraters. Inputs uprated by CPI-U keep the default path too. The SOI income
totals keep their CBO values through 2036. Inputs uprated by
``calibration.gov.cbo.income_by_source.adjusted_gross_income`` or its
per-capita series keep the default path: 348 variables, including 16 stored
in the default dataset. From 2036 to 2100, that path grows 10.393 times per
capita, versus 9.418 for wages.

A ``Microsimulation`` built from a single-year dataset calls
``extend_single_year_dataset`` without ``system=``, so the default system ages
that dataset. By default the extension runs through the last year in the
CPI-U YAML, 2036, and inputs age on the default paths through that year. For
a later year core uprates each input whose variable names an ``uprating``
parameter from its 2036 value on the reformed system's path, so that year
carries only the gap accumulated by 2036. The SOI totals keep their CBO values
through 2036 here, so the gap falls on the input that reads
``gov.ssa.uprating`` directly, ``veterans_benefits``: the index reads 403.287
by default against 407.218 here at 2036, a ratio of 0.990347. To age inputs
on these paths, pass a dataset that ``extend_single_year_dataset`` extended
with the reformed system.

Order with other reforms. The assumption rewrites the parameters above for
years after their last published values, so list it before any policy reform
that sets one of them. A built system applies its reform set twice, so with
``trustees_core_thresholds_reform`` either order wage-indexes the IRS
thresholds on the 2026 Trustees NAWI. The order rule keeps the parameters a
later reform overrides directly; it doesn't re-derive their readers. An
override of ``gov.ssa.uprating`` after the assumption moves
``veterans_benefits``, which reads the index when it runs, and leaves the SSI
amounts derived from the index alone.
"""

from __future__ import annotations

from typing import Any

from policyengine_core.parameters.operations.get_parameter import get_parameter
from policyengine_core.parameters.operations.uprate_parameters import (
    normalize_uprating_metadata,
    round_uprated_value,
)
from policyengine_core.periods import instant

from policyengine_us.model_api import Reform
from policyengine_us.parameters.uprating_extensions import (
    extend_social_security_payroll_cap,
    extend_social_security_wage_indexed_parameters,
)
from policyengine_us.reforms.ssa.trustees_2025 import (
    apply_trustees_2025_soi_income_projection,
)
from policyengine_us.reforms.ssa.trustees_core_thresholds import (
    _iter_updatable_parameters,
)


TRUSTEES_2026_ECONOMIC_ASSUMPTION: dict[str, Any] = {
    "name": "trustees-2026-economic-v1",
    "description": (
        "SSA 2026 Trustees intermediate projections of the national average "
        "wage index and the CPI behind benefit COLAs, chained onto published "
        "values, for explicit long-range scoring scenarios."
    ),
    "source": (
        "SSA 2026 Trustees Report, single-year tables, Table VI.G1 "
        "(intermediate assumptions)"
    ),
    "url": "https://www.ssa.gov/oact/TR/2026/SingleYearTRTables_TR2026.xlsx",
    "start_year": 2026,
    "end_year": 2100,
    "not_default_current_law": True,
}

# SSA publishes NAWI with a two-year lag; NAWI(2025) is the last published.
TRUSTEES_2026_LAST_PUBLISHED_NAWI_YEAR = 2025
# gov.ssa.uprating at 2027-01-01 holds the 2026 third-quarter CPI-W actual.
TRUSTEES_2026_LAST_ACTUAL_SSA_UPRATING_YEAR = 2027
# SSA last determined the contribution and benefit base for 2027.
TRUSTEES_2026_LAST_DETERMINED_CAP_YEAR = 2027
# The SOI income totals follow CBO's income projections through 2036.
TRUSTEES_2026_LAST_CBO_SOI_YEAR = 2036

# 2026 Trustees Report, single-year tables, Table VI.G1, intermediate
# assumptions: the average wage index (AWI) for each calendar year.
TRUSTEES_2026_AVERAGE_WAGE_INDEX: dict[int, float] = {
    2025: 72_025.07,
    2026: 75_246.70,
    2027: 78_286.92,
    2028: 81_537.43,
    2029: 85_047.82,
    2030: 88_895.99,
    2031: 92_915.31,
    2032: 96_989.47,
    2033: 101_085.63,
    2034: 105_045.59,
    2035: 109_064.86,
    2036: 113_112.48,
    2037: 117_242.36,
    2038: 121_528.53,
    2039: 125_983.85,
    2040: 130_576.20,
    2041: 135_325.06,
    2042: 140_239.16,
    2043: 145_313.35,
    2044: 150_555.40,
    2045: 155_964.90,
    2046: 161_545.30,
    2047: 167_321.25,
    2048: 173_286.57,
    2049: 179_452.26,
    2050: 185_819.54,
    2051: 192_394.84,
    2052: 199_198.57,
    2053: 206_238.61,
    2054: 213_512.79,
    2055: 221_029.75,
    2056: 228_806.23,
    2057: 236_861.66,
    2058: 245_212.23,
    2059: 253_867.58,
    2060: 262_840.05,
    2061: 272_142.40,
    2062: 281_795.18,
    2063: 291_797.67,
    2064: 302_159.97,
    2065: 312_892.87,
    2066: 324_008.11,
    2067: 335_532.36,
    2068: 347_462.71,
    2069: 359_822.61,
    2070: 372_632.16,
    2071: 385_893.43,
    2072: 399_613.46,
    2073: 413_814.19,
    2074: 428_542.36,
    2075: 443_807.74,
    2076: 459_625.45,
    2077: 476_013.42,
    2078: 492_973.99,
    2079: 510_532.72,
    2080: 528_702.70,
    2081: 547_536.96,
    2082: 567_045.63,
    2083: 587_262.55,
    2084: 608_220.24,
    2085: 629_920.13,
    2086: 652_435.35,
    2087: 675_715.06,
    2088: 699_838.74,
    2089: 724_829.80,
    2090: 750_695.44,
    2091: 777_483.52,
    2092: 805_213.29,
    2093: 833_926.24,
    2094: 863_653.71,
    2095: 894_429.45,
    2096: 926_285.91,
    2097: 959_260.74,
    2098: 993_393.76,
    2099: 1_028_721.72,
    2100: 1_065_285.35,
}

# The same table's adjusted CPI (2026 = 100), an annual average for each
# calendar year.
TRUSTEES_2026_ADJUSTED_CPI: dict[int, float] = {
    2025: 97.45,
    2026: 100.00,
    2027: 102.46,
    2028: 104.92,
    2029: 107.44,
    2030: 110.02,
    2031: 112.66,
    2032: 115.36,
    2033: 118.13,
    2034: 120.97,
    2035: 123.87,
    2036: 126.84,
    2037: 129.89,
    2038: 133.00,
    2039: 136.20,
    2040: 139.46,
    2041: 142.81,
    2042: 146.24,
    2043: 149.75,
    2044: 153.34,
    2045: 157.02,
    2046: 160.79,
    2047: 164.65,
    2048: 168.60,
    2049: 172.65,
    2050: 176.79,
    2051: 181.03,
    2052: 185.38,
    2053: 189.83,
    2054: 194.38,
    2055: 199.05,
    2056: 203.83,
    2057: 208.72,
    2058: 213.73,
    2059: 218.86,
    2060: 224.11,
    2061: 229.49,
    2062: 235.00,
    2063: 240.64,
    2064: 246.41,
    2065: 252.33,
    2066: 258.38,
    2067: 264.58,
    2068: 270.93,
    2069: 277.43,
    2070: 284.09,
    2071: 290.91,
    2072: 297.89,
    2073: 305.04,
    2074: 312.36,
    2075: 319.86,
    2076: 327.54,
    2077: 335.40,
    2078: 343.45,
    2079: 351.69,
    2080: 360.13,
    2081: 368.77,
    2082: 377.62,
    2083: 386.69,
    2084: 395.97,
    2085: 405.47,
    2086: 415.20,
    2087: 425.17,
    2088: 435.37,
    2089: 445.82,
    2090: 456.52,
    2091: 467.48,
    2092: 478.70,
    2093: 490.19,
    2094: 501.95,
    2095: 514.00,
    2096: 526.33,
    2097: 538.96,
    2098: 551.90,
    2099: 565.14,
    2100: 578.71,
}


def _check_end_year(end_year: int, first_year: int, last_year: int) -> None:
    if not first_year <= end_year <= last_year:
        raise ValueError(
            f"The SSA Trustees 2026 assumptions run from {first_year} to "
            f"{last_year}; end_year {end_year} falls outside them."
        )


def _set_annual_values(parameter, values_by_year: dict[int, float]) -> None:
    """Set each year's value, then hold the last after it."""
    for year, value in values_by_year.items():
        parameter.update(period=f"year:{year}-01-01:1", value=value)
    end_year = max(values_by_year)
    parameter.update(
        start=instant(f"{end_year}-01-01"),
        value=values_by_year[end_year],
    )


def apply_trustees_2026_nawi_projection(
    parameters,
    *,
    end_year: int = 2100,
) -> None:
    """Chain the Trustees' AWI growth onto the published NAWI(2025)."""
    first_year = TRUSTEES_2026_LAST_PUBLISHED_NAWI_YEAR + 1
    _check_end_year(end_year, first_year, max(TRUSTEES_2026_AVERAGE_WAGE_INDEX))
    nawi = parameters.gov.ssa.nawi
    awi = TRUSTEES_2026_AVERAGE_WAGE_INDEX
    value = float(nawi(f"{TRUSTEES_2026_LAST_PUBLISHED_NAWI_YEAR}-01-01"))
    values_by_year = {}
    for year in range(first_year, end_year + 1):
        value *= awi[year] / awi[year - 1]
        values_by_year[year] = value
    _set_annual_values(nawi, values_by_year)


def apply_trustees_2026_price_projection(
    parameters,
    *,
    end_year: int = 2100,
) -> None:
    """Chain the Trustees' CPI growth onto the last actual COLA index.

    ``gov.ssa.uprating`` at Y-01-01 holds the third-quarter CPI-W of Y - 1.
    The Trustees publish annual averages, so the annual change in the
    adjusted CPI from Y - 2 to Y - 1 stands in for the third-quarter change.
    """
    first_year = TRUSTEES_2026_LAST_ACTUAL_SSA_UPRATING_YEAR + 1
    _check_end_year(end_year, first_year, max(TRUSTEES_2026_ADJUSTED_CPI) + 1)
    uprating = parameters.gov.ssa.uprating
    cpi = TRUSTEES_2026_ADJUSTED_CPI
    value = float(uprating(f"{TRUSTEES_2026_LAST_ACTUAL_SSA_UPRATING_YEAR}-01-01"))
    values_by_year = {}
    for year in range(first_year, end_year + 1):
        value *= cpi[year - 1] / cpi[year - 2]
        values_by_year[year] = value
    _set_annual_values(uprating, values_by_year)


# Each path's last unchanged year: readers keep their values through it.
TRUSTEES_2026_PATHS: dict[str, int] = {
    "gov.ssa.nawi": TRUSTEES_2026_LAST_PUBLISHED_NAWI_YEAR,
    "gov.ssa.uprating": TRUSTEES_2026_LAST_ACTUAL_SSA_UPRATING_YEAR,
}

# Readers of a path that another step derives, so step 2 leaves them alone.
_DERIVED_ELSEWHERE = ("gov.irs.payroll.social_security.cap",)


def trustees_2026_path_readers(parameters) -> dict[str, list]:
    """Parameters whose ``uprating`` metadata names each Trustees path."""
    return {
        path: [
            parameter
            for parameter in _iter_updatable_parameters(
                parameters, uprating_parameter=path
            )
            if parameter.name not in _DERIVED_ELSEWHERE
        ]
        for path in TRUSTEES_2026_PATHS
    }


def _rederive_reader(
    parameter,
    path,
    *,
    last_unchanged_year: int,
    end_year: int,
) -> None:
    """Uprate a reader from the new path as core's ``uprate_parameter`` does.

    Core takes the reader's last value, at instant L, and sets each later
    year to that value times path(Y) / path(L), rounded as the metadata says.
    Only values after ``last_unchanged_year`` change; those the YAML states
    stay as stated.
    """
    meta = normalize_uprating_metadata(parameter.metadata["uprating"])
    if "at_defined_interval" in meta or "start_instant" in meta:
        raise ValueError(
            f"{parameter.name} uprates by {path.name} on a cadence or from a "
            "set instant, which the SSA Trustees 2026 assumptions don't "
            "re-derive."
        )
    stated = [
        value.instant_str
        for value in parameter.values_list
        if value.file_path is not None
    ]
    if not stated:
        raise ValueError(f"{parameter.name} has no value from its YAML file.")
    last_stated = max(stated)
    if last_stated >= f"{last_unchanged_year + 1}-01-01":
        raise ValueError(
            f"{parameter.name} states a value for {last_stated}, after "
            f"{path.name}'s last unchanged year, {last_unchanged_year}."
        )
    value_at_start = parameter(last_stated)
    path_at_start = path(last_stated)
    values_by_year = {}
    for year in range(last_unchanged_year + 1, end_year + 1):
        # Core's operation order, so an unchanged path gives core's value.
        value = value_at_start * (path(f"{year}-01-01") / path_at_start)
        if "rounding" in meta:
            value = round_uprated_value(meta, value)
        values_by_year[year] = value
    _set_annual_values(parameter, values_by_year)


def apply_trustees_2026_path_readers(
    parameters,
    *,
    end_year: int = 2100,
) -> None:
    """Re-derive the parameters core uprated from the old paths at build."""
    for path_name, readers in trustees_2026_path_readers(parameters).items():
        path = get_parameter(parameters, path_name)
        for parameter in readers:
            _rederive_reader(
                parameter,
                path,
                last_unchanged_year=TRUSTEES_2026_PATHS[path_name],
                end_year=end_year,
            )


def apply_trustees_2026_economic_assumptions(
    parameters,
    *,
    end_year: int = 2100,
) -> None:
    """Put Social Security's wage and price paths on the 2026 Trustees'."""
    _check_end_year(
        end_year,
        TRUSTEES_2026_LAST_ACTUAL_SSA_UPRATING_YEAR + 1,
        max(TRUSTEES_2026_AVERAGE_WAGE_INDEX),
    )
    apply_trustees_2026_nawi_projection(parameters, end_year=end_year)
    apply_trustees_2026_price_projection(parameters, end_year=end_year)
    # Reads the active NAWI, so the income totals follow the new path. The
    # helper holds each total at its end_year value from end_year on, so for
    # an end_year of 2036 or earlier it would overwrite CBO's later values.
    if end_year > TRUSTEES_2026_LAST_CBO_SOI_YEAR:
        apply_trustees_2025_soi_income_projection(
            parameters,
            last_projected_year=TRUSTEES_2026_LAST_CBO_SOI_YEAR,
            end_year=end_year,
        )
    extend_social_security_payroll_cap(
        parameters,
        last_projected_year=TRUSTEES_2026_LAST_DETERMINED_CAP_YEAR,
        end_year=end_year,
    )
    # Extend the owners' draw copy on the same rule from its own values
    # through 2027, not from the live cap, so a policy reform's cap from 2027
    # can't become the copy's no-decrease floor when the reform set runs again.
    extend_social_security_payroll_cap(
        parameters,
        last_projected_year=TRUSTEES_2026_LAST_DETERMINED_CAP_YEAR,
        end_year=end_year,
        cap=parameters.gov.contrib.ssa.owners_draw.current_law_cap,
    )
    extend_social_security_wage_indexed_parameters(parameters, end_year=end_year)
    apply_trustees_2026_path_readers(parameters, end_year=end_year)


def create_trustees_2026_economic_assumptions_reform(
    *,
    end_year: int = 2100,
) -> Reform:
    """Return a reform that applies the 2026 Trustees' wage and price paths.

    This is an explicit scenario assumption for long-range scoring, not
    default current law.
    """
    _check_end_year(
        end_year,
        TRUSTEES_2026_LAST_ACTUAL_SSA_UPRATING_YEAR + 1,
        max(TRUSTEES_2026_AVERAGE_WAGE_INDEX),
    )

    def modify_parameters(parameters):
        apply_trustees_2026_economic_assumptions(parameters, end_year=end_year)
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


trustees_2026_economic_assumptions_reform = (
    create_trustees_2026_economic_assumptions_reform()
)
