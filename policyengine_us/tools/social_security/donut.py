"""Separate annual above-threshold tax and optional benefit-credit streams.

The fixed-threshold 2025 OACT E2.13/E2.14 variants remain separate parameter
sets. This service supplies a ledger for the household calculator, rather
than changing population payroll-tax variables or ordinary covered earnings.

https://www.ssa.gov/OACT/solvency/provisions_tr2025/payrolltax.html
"""

from dataclasses import dataclass
from fractions import Fraction

from .pia import Number, _number


DONUT_VARIANTS = ("oact_2025_e2_13", "oact_2025_e2_14", "custom")


@dataclass(frozen=True)
class DonutParameters:
    """One independently named annual provision; activation defaults off.

    Amounts entering covered SE or owners' draw must already use their net
    earnings adjustments. Including either stream applies identically on the
    tax and benefit sides. The dated threshold is explicit: the archived OACT
    variants hold it fixed, while callers may supply a custom annual path.
    """

    name: str = "custom"
    in_effect: bool = False
    start_year: int = 2027
    threshold: Number = 0
    tax_rate: Number = 0
    credit_enabled: bool = False
    credit_rate: Number = 0
    include_self_employment: bool = True
    include_owners_draw: bool = True


@dataclass(frozen=True)
class DonutYearResult:
    taxed_earnings: Fraction
    credited_earnings: Fraction
    tax: Fraction
    threshold: Fraction


def compute_donut_year(
    year: int,
    *,
    covered_wages: Number,
    ordinary_cap: Number,
    existing_covered_se: Number = 0,
    owners_draw_net_earnings: Number = 0,
    parameters: DonutParameters = DonutParameters(),
) -> DonutYearResult:
    """Tax only selected earnings above max(ordinary cap, donut threshold).

    Covered wages, existing covered SE, and newly reclassified net draw are
    disjoint annual inputs. Credited earnings equal the taxed stream when
    credit is enabled; they are zero otherwise. No tax dollars are converted
    into earnings credit. The ordinary AIME ledger is left to the caller.
    """
    p = parameters
    if isinstance(year, bool) or not isinstance(year, int):
        raise ValueError("earnings year must be an integer calendar year")
    if isinstance(p.start_year, bool) or not isinstance(p.start_year, int):
        raise ValueError("donut start_year must be an integer calendar year")
    cap = _number(ordinary_cap, "ordinary annual cap")
    threshold = _number(p.threshold, "donut threshold")
    tax_rate = _number(p.tax_rate, "donut tax rate")
    credit_rate = _number(p.credit_rate, "donut credit rate")
    wages = _number(covered_wages, "covered wages")
    se = _number(existing_covered_se, "existing covered SE")
    draw = _number(owners_draw_net_earnings, "owners' net draw")
    if min(cap, threshold, tax_rate, credit_rate, wages, se, draw) < 0:
        raise ValueError("donut amounts and rates must be nonnegative")
    tier_start = max(cap, threshold)
    if not p.in_effect or year < p.start_year or tax_rate == 0:
        return DonutYearResult(Fraction(0), Fraction(0), Fraction(0), tier_start)
    earnings = wages
    if p.include_self_employment:
        earnings += se
    if p.include_owners_draw:
        earnings += draw
    taxed = max(Fraction(0), earnings - tier_start)
    credited = taxed if p.credit_enabled else Fraction(0)
    return DonutYearResult(taxed, credited, taxed * tax_rate, tier_start)


def donut_parameters_at(parameters, year: int, variant: str) -> DonutParameters:
    """Resolve one named annual parameter set without collapsing variants."""
    if variant not in DONUT_VARIANTS:
        raise ValueError(f"Unknown donut variant: {variant}")
    node = getattr(parameters.gov.contrib.ssa.history.donut, variant)
    settings = node(f"{year}-01-01")
    return DonutParameters(
        name=variant,
        in_effect=bool(settings.in_effect),
        start_year=int(settings.start_year),
        threshold=settings.threshold,
        tax_rate=settings.tax_rate,
        credit_enabled=bool(settings.credit_enabled),
        credit_rate=settings.credit_rate,
        include_self_employment=bool(settings.include_self_employment),
        include_owners_draw=bool(settings.include_owners_draw),
    )
