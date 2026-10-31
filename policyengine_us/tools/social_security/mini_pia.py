"""Annual mini-PIAs for the opt-in covered-earnings history route.

OACT's archived 2025 B3.12 specifies the highest 40 annual mini-PIAs and the
fixed divisor 37. Keeping annual and blended values exact until the combined
eligibility PIA's final dime truncation is an explicit modeling convention.

https://www.ssa.gov/OACT/solvency/provisions_tr2025/benefitlevel.html
"""

from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction

from .pia import (
    DEFAULT_FACTORS,
    FormulaPath,
    Number,
    _number,
    _year,
    compute_pia,
)


@dataclass(frozen=True)
class MiniPIAResult:
    """Unrounded annual values retain the supplied earnings-ledger order."""

    annual_mini_pias: tuple[Fraction, ...]
    selected_mini_pias: tuple[Fraction, ...]
    mini_pia: Fraction


def compute_mini_pia(
    indexed_annual_amounts: Iterable[Number],
    eligibility_year: int,
    *,
    bend_points: tuple[Number, Number],
    factors: tuple[Number, Number, Number] = DEFAULT_FACTORS,
    formula_path: FormulaPath | None = None,
    payment_year: int | None = None,
    recompute_mode: str = "cohort",
) -> MiniPIAResult:
    """Apply E's shared PIA formula to every indexed annual amount / 12.

    Select annual mini-PIAs themselves, pad the selected list to 40 with
    certified zeros, and always divide their exact sum by 37. The history
    caller is responsible for refusing uncertified missing earnings years.
    """
    _year(eligibility_year, "eligibility year")
    annual = tuple(
        compute_pia(
            _number(amount, "indexed annual earnings") / 12,
            eligibility_year,
            formula_path,
            payment_year,
            recompute_mode,
            bend_points=bend_points,
            factors=factors,
            round_result=False,
            exact_result=True,
        )
        for amount in indexed_annual_amounts
    )
    # Validate the shared formula even for an empty, certified-zero career.
    if not annual:
        compute_pia(
            0,
            eligibility_year,
            formula_path,
            payment_year,
            recompute_mode,
            bend_points=bend_points,
            factors=factors,
        )
    selected = tuple(sorted(annual, reverse=True)[:40])
    selected += (Fraction(0),) * (40 - len(selected))
    return MiniPIAResult(
        annual_mini_pias=annual,
        selected_mini_pias=selected,
        mini_pia=sum(selected, Fraction(0)) / 37,
    )


def blend_mini_pia(
    conventional_pia: Number,
    mini_pia: Number,
    share: Number,
    *,
    disability: bool = False,
) -> Fraction:
    """Blend unrounded mini and dime-rounded conventional PIA exactly once.

    Disability remains conventional regardless of the retired-worker share.
    A separately enabled AIME+ component is added after this blend, before
    final eligibility-PIA dime truncation by the household payment pipeline.
    """
    conventional = _number(conventional_pia, "conventional PIA")
    mini = _number(mini_pia, "mini-PIA")
    fraction = _number(share, "mini-PIA share")
    if conventional < 0 or mini < 0:
        raise ValueError("PIAs must be nonnegative")
    if not 0 <= fraction <= 1:
        raise ValueError("mini-PIA share must be between zero and one")
    return (
        conventional if disability else fraction * mini + (1 - fraction) * conventional
    )


def mini_pia_share_at(
    parameters, eligibility_year: int, *, disability=False
) -> Fraction:
    """Read the retired-worker cohort share; master activation defaults off."""
    year = _year(eligibility_year, "eligibility year")
    settings = parameters.gov.contrib.ssa.history.mini_pia(f"{year}-01-01")
    if disability or not settings.in_effect:
        return Fraction(0)
    share = _number(settings.share, "mini-PIA share")
    if not 0 <= share <= 1:
        raise ValueError("mini-PIA share must be between zero and one")
    return share
