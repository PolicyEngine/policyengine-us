"""The BLS CPI files carry published monthly actuals through June 2026,
including the October 2025 gap (never published) and the replaced
projection points (#9091)."""

from decimal import ROUND_HALF_UP, Decimal

import yaml

from policyengine_us.system import system


def _cpi(name):
    return getattr(system.parameters.gov.bls.cpi, name)


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


def test_cpi_u_monthly_actuals():
    cpi_u = _cpi("cpi_u")
    assert cpi_u("2026-06-01") == 332.568
    assert cpi_u("2025-10-01") == 324.245
    assert cpi_u("2026-02-01") == 327.460


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
    ssa_uprating = _listed_values(system.parameters.gov.ssa.uprating)
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
