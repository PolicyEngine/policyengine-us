"""Check published monthly CPI values and the forecast boundary."""

from decimal import ROUND_HALF_UP, Decimal
from functools import lru_cache
from pathlib import Path

import pytest
import yaml

from policyengine_core.parameters import load_parameter_file


PARAMETERS_PATH = Path(__file__).resolve().parents[5] / "parameters"


@lru_cache(maxsize=4)
def _parameter(relative_path):
    return load_parameter_file(str(PARAMETERS_PATH / relative_path))


def _cpi(name):
    return _parameter(f"gov/bls/cpi/{name}.yaml")


def test_cpi_w_monthly_actuals():
    cpi_w = _cpi("cpi_w")
    # June 2026 observed value (CWUR0000SA0, not seasonally adjusted).
    assert cpi_w("2026-06-01") == 327.075
    # October 2025 was never published: September carries forward.
    assert cpi_w("2025-10-01") == 318.139
    # The observed February replaces the derived 2026Q1 projection point.
    assert cpi_w("2026-02-01") == 319.422
    # The seasonally adjusted series (CWSR0000SA0) reads 303.623 here.
    assert cpi_w("2024-01-01") == 302.201


@pytest.mark.parametrize(
    "month, expected",
    [
        ("2024-01-01", 308.417),
        ("2024-02-01", 310.326),
        ("2024-03-01", 312.332),
        ("2024-04-01", 313.548),
        ("2024-05-01", 314.069),
        ("2024-06-01", 314.175),
        ("2024-07-01", 314.540),
        ("2024-08-01", 314.796),
        ("2024-09-01", 315.301),
        ("2024-10-01", 315.664),
        ("2024-11-01", 315.493),
        ("2024-12-01", 315.605),
        ("2025-01-01", 317.671),
        ("2025-02-01", 319.082),
        ("2025-03-01", 319.799),
        ("2025-04-01", 320.795),
        ("2025-05-01", 321.465),
        ("2025-06-01", 322.561),
        ("2025-07-01", 323.048),
        ("2025-08-01", 323.976),
        ("2025-09-01", 324.800),
        ("2025-11-01", 324.122),
        ("2025-12-01", 324.054),
        ("2026-01-01", 325.252),
        ("2026-02-01", 326.785),
        ("2026-03-01", 330.213),
        ("2026-04-01", 333.020),
        ("2026-05-01", 335.123),
        ("2026-06-01", 333.952),
        ("2026-07-01", 333.918),
        ("2026-08-01", 334.980),
        ("2026-09-01", 336.940),
        ("2026-10-01", 337.511),
    ],
)
def test_cpi_u_monthly_actuals(month, expected):
    """Check the monthly CPI-U values BLS publishes without seasonal adjustment."""
    cpi_u = _cpi("cpi_u")
    assert _listed_values(cpi_u)[month] == expected
    assert cpi_u(month) == expected


def test_cpi_u_carries_september_forward_for_unpublished_october_2025():
    cpi_u = _cpi("cpi_u")
    assert "2025-10-01" not in _listed_values(cpi_u)
    assert cpi_u("2025-10-01") == cpi_u("2025-09-01") == 324.800


@pytest.mark.parametrize("year, expected", [(2024, "310.955"), (2025, "319.205")])
def test_cpi_u_twelve_month_averages_ending_august(year, expected):
    cpi_u = _cpi("cpi_u")
    months = [f"{year - 1}-{month:02d}-01" for month in range(9, 13)] + [
        f"{year}-{month:02d}-01" for month in range(1, 9)
    ]
    average = sum(Decimal(str(cpi_u(month))) for month in months) / 12
    assert average == Decimal(expected)


def test_cpi_u_keeps_the_cbo_projection_after_the_latest_actual():
    cpi_u = _cpi("cpi_u")
    listed_values = _listed_values(cpi_u)
    assert listed_values["2026-10-01"] == 337.511
    next_instant = min(instant for instant in listed_values if instant > "2026-10-01")
    assert next_instant == "2027-02-01"
    assert listed_values[next_instant] == 340.3
    assert cpi_u(next_instant) == 340.3
    references = cpi_u.metadata["reference"]
    assert any(
        reference["href"] == "https://data.bls.gov/timeseries/CUUR0000SA0"
        and "not seasonally adjusted" in reference["title"]
        for reference in references
    )
    assert all("CUSR0000SA0" not in reference["href"] for reference in references)


def test_c_cpi_u_monthly_actuals():
    c_cpi_u = _cpi("c_cpi_u")
    assert c_cpi_u("2026-06-01") == 184.992
    assert c_cpi_u("2025-10-01") == 180.196
    # The observed February replaces the annual projection point (183.1).
    assert c_cpi_u("2026-02-01") == 181.080


def _listed_values(parameter):
    """The dated values a parameter's YAML file lists, before the system
    backdates the first one and extends the series."""
    with open(parameter.file_path) as file:
        values = yaml.safe_load(file)["values"]
    return {str(instant): value for instant, value in values.items()}


def _rounded_percent_increase(new, old):
    """Percentage increase rounded to the nearest tenth, per 415(i)(1)(D)."""
    percent = Decimal(repr(new)) / Decimal(repr(old)) * 100 - 100
    return percent.quantize(Decimal("0.1"), ROUND_HALF_UP)


def test_cpi_w_third_quarter_averages_reproduce_ssa_uprating():
    """CPI-W is one series: the not seasonally adjusted index SSA uses.

    gov.ssa.uprating holds the CPI-W third-quarter average (42 U.S.C.
    415(i)(1)(A)(i) and (G)) of the latest cost-of-living computation
    quarter. A quarter whose CPI increase, rounded to the nearest tenth of a
    percent (415(i)(1)(D)), is not above zero is not one (415(i)(1)(B)), so
    the level carries forward. Each year whose July-September the CPI-W file
    lists as monthly values must reproduce SSA's value to its three
    published decimals. The seasonally adjusted values the file held for
    2024 failed this: they put the 2024Q3 average at 307.931, not 308.729.
    """
    cpi_w = _listed_values(_cpi("cpi_w"))
    ssa_uprating = _listed_values(_parameter("gov/ssa/uprating.yaml"))
    checked = []
    prior_level = None
    for instant in sorted(ssa_uprating):
        year = int(instant[:4])
        months = [f"{year - 1}-{month:02d}-01" for month in (7, 8, 9)]
        if not all(month in cpi_w for month in months):
            # CBO-based projections from here on.
            break
        average = sum(cpi_w[month] for month in months) / 3
        level = ssa_uprating[instant]
        if prior_level is None or _rounded_percent_increase(average, prior_level) > 0:
            assert abs(level - average) < 0.0005 + 1e-9, (
                f"gov.ssa.uprating {year} is {level}, but the {year - 1} "
                f"third-quarter CPI-W average is {average:.4f}."
            )
        else:
            assert level == prior_level, (
                f"No cost-of-living increase for {year}, so gov.ssa.uprating "
                f"should stay at {prior_level}, not {level}."
            )
        prior_level = level
        checked.append(year)
    # The 2022-2026 actuals, through the 2025Q3 average SSA used for 2026.
    assert set(range(2022, 2027)) <= set(checked), checked
