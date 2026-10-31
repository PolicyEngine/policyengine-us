"""Infer an eligibility-cohort AIME from an annual reported benefit.

This is the population, proportional-change approximation. It does not recover
an unidentified monthly payment history or undo earnings-test withholding,
dual entitlement or a binding family maximum. Callers must identify the worker,
claiming adjustment and auxiliary share before using it. Both the reform and
baseline PIAs use the shared household calculator's formula and dime rounding.
The inverse always uses the supplied *unreformed* historical scale.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, localcontext
from fractions import Fraction

from policyengine_us.tools.social_security.pia import (
    DEFAULT_FACTORS,
    FormulaPath,
    Number,
    compute_pia,
    has_active_reform,
    inverse_pia,
    inverse_unrounded,
)


@dataclass(frozen=True)
class RatioResult:
    """A ratio and monthly-dollar inference diagnostics for one annual record.

    ``aime`` is the baseline inverse at the observed eligibility PIA. For an
    exact eligibility PIA it is the lower endpoint of the half-open interval
    ``[aime_lower, aime_upper)``. Survey observations instead give a conditional
    interval, with additional measurement error explicitly flagged. Endpoints
    are represented as 50-digit Decimals rounded toward positive infinity;
    exact rational endpoints are retained internally for forward computation.
    Zero and unsupported pre-1983 records have factor 1 and zero diagnostics.
    """

    factor: Decimal
    aime: Decimal
    aime_lower: Decimal
    aime_upper: Decimal
    pre1983: bool = False
    measurement_uncertainty: bool = False


def _number(value: Number, name: str) -> Fraction:
    try:
        if isinstance(value, bool):
            raise ValueError
        if isinstance(value, Fraction):
            return value
        result = Decimal(str(value))
        if not result.is_finite():
            raise ValueError
        return Fraction(result)
    except (ValueError, TypeError, ArithmeticError) as error:
        raise ValueError(f"{name} must be a finite number") from error


def _decimal(value: Fraction, *, ceiling: bool = False) -> Decimal:
    with localcontext() as context:
        context.prec = 50
        if ceiling:
            context.rounding = ROUND_CEILING
        return Decimal(value.numerator) / Decimal(value.denominator)


def compute_pia_ratio(
    annual_benefit: Number,
    eligibility_year: int,
    formula_path: FormulaPath | None = None,
    payment_year: int | None = None,
    recompute_mode: str = "cohort",
    *,
    bend_points: tuple[Number, Number],
    claiming_adjustment: Number = 1,
    auxiliary_share: Number = 1,
    cola_factor: Number = 1,
    factors: tuple[Number, Number, Number] = DEFAULT_FACTORS,
    exact_eligibility_pia: bool = False,
    annual_rounding_bound: Number = 0,
) -> RatioResult:
    """Return ``P_new(A, E; t) / P_old(A, E)`` for a reported annual benefit.

    The inferred monthly eligibility PIA is
    ``annual_benefit / (12 * claiming_adjustment * auxiliary_share * cola_factor)``.
    ``cola_factor`` must be the unreformed accumulation from eligibility, and
    ``annual_benefit`` must be the unreformed reported amount. A supplied
    composite survivor ratio belongs in either adjustment argument, once.

    Set ``exact_eligibility_pia=True`` only when the backwards-derived amount
    is an exact dime-rounded eligibility PIA. Otherwise the point estimate is
    the unrounded baseline inverse, and the interval extends through the
    inverse at ``z + .10``. It is conditional on the observed survey amount;
    ``measurement_uncertainty`` remains true even if z happens to be a dime.
    An optional nonnegative ``annual_rounding_bound`` expands the annual
    observation to ``[max(0, b-bound), b+bound)`` before dividing by 12*a*s*C.
    The upper end additionally allows one dime of initial PIA truncation.
    This conservative interval does not represent other survey measurement
    errors or unidentified monthly payment rounding. It cannot be combined
    with the exact-PIA assertion.

    Pre-1983 benchmark records remain unchanged because the historical
    upward-rounding method is unsupported. Negative/nonfinite benefits and
    nonpositive/nonfinite adjustment, share or COLA inputs are rejected.
    """
    benefit = _number(annual_benefit, "annual reported benefit")
    if benefit < 0:
        raise ValueError("annual reported benefit must be nonnegative")
    adjustments = tuple(
        _number(value, name)
        for value, name in (
            (claiming_adjustment, "claiming adjustment"),
            (auxiliary_share, "auxiliary share"),
            (cola_factor, "baseline COLA factor"),
        )
    )
    if any(value <= 0 for value in adjustments):
        raise ValueError(
            "claiming adjustment, auxiliary share and COLA factor must be positive"
        )
    bound = _number(annual_rounding_bound, "annual rounding bound")
    if bound < 0:
        raise ValueError("annual rounding bound must be nonnegative")
    if exact_eligibility_pia and bound:
        raise ValueError("exact eligibility PIA cannot have an annual rounding bound")
    if isinstance(eligibility_year, bool) or not isinstance(eligibility_year, int):
        raise ValueError("eligibility year must be an integer calendar year")
    neutral = RatioResult(Decimal(1), Decimal(0), Decimal(0), Decimal(0))
    if eligibility_year < 1983:
        return RatioResult(
            neutral.factor,
            neutral.aime,
            neutral.aime_lower,
            neutral.aime_upper,
            pre1983=True,
        )
    if benefit == 0:
        return neutral

    divisor = 12 * adjustments[0] * adjustments[1] * adjustments[2]
    pia = benefit / divisor
    if exact_eligibility_pia or (pia * 10).denominator == 1:
        interval = inverse_pia(
            pia, eligibility_year, bend_points=bend_points, factors=factors
        )
        point = interval.exact_lower
        lower, upper = interval.exact_lower, interval.exact_upper
    else:
        point = inverse_unrounded(
            pia, eligibility_year, bend_points=bend_points, factors=factors
        )
        lower = point
        upper = inverse_unrounded(
            pia + Fraction(1, 10),
            eligibility_year,
            bend_points=bend_points,
            factors=factors,
        )
    if bound:
        lower = inverse_unrounded(
            max(0, benefit - bound) / divisor,
            eligibility_year,
            bend_points=bend_points,
            factors=factors,
        )
        upper = inverse_unrounded(
            (benefit + bound) / divisor + Fraction(1, 10),
            eligibility_year,
            bend_points=bend_points,
            factors=factors,
        )

    active = has_active_reform(
        formula_path, eligibility_year, payment_year, recompute_mode
    )
    old = compute_pia(
        point,
        eligibility_year,
        payment_year=payment_year,
        recompute_mode=recompute_mode,
        bend_points=bend_points,
        factors=factors,
        round_result=True,
    )
    new = compute_pia(
        point,
        eligibility_year,
        formula_path,
        payment_year,
        recompute_mode,
        bend_points=bend_points,
        factors=factors,
        round_result=True,
    )
    if (active or old != new) and old <= 0:
        raise ValueError("inferred baseline PIA must be positive for a PIA ratio")
    factor = Decimal(1)
    if old != new:
        factor = _decimal(Fraction(new) / Fraction(old))
    return RatioResult(
        factor=factor,
        aime=_decimal(point, ceiling=True),
        aime_lower=_decimal(lower, ceiling=True),
        aime_upper=_decimal(upper, ceiling=True),
        measurement_uncertainty=not exact_eligibility_pia,
    )
