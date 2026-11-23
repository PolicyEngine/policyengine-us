"""Eligibility-cohort Primary Insurance Amount formulas, in monthly dollars.

The ordinary model's reported-benefit route does not call this opt-in service.
Callers supply the unreformed bend points at initial eligibility, even when a
payment-year reform recomputes an older cohort. Benchmark years before 1983
are unsupported because their initial-PIA rounding rule differs.

Sources:
* https://www.ssa.gov/OACT/COLA/piaformula.html
* https://secure.ssa.gov/poms.nsf/lnx/0300605021
* https://www.congress.gov/bill/119th-congress/senate-bill/770/text
* https://www.ssa.gov/OACT/solvency/advisoryboard_20050810.pdf

Composition order is custom bend points/factors, S.770, full price indexing,
progressive price indexing, then one final dime truncation. Price-index scales,
maximum-career AIME and maximum-PIA targets must be frozen externally with
their index bases, lags and source provenance. No sample percentile is inferred.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, localcontext
from fractions import Fraction
from typing import Mapping


Number = Decimal | Fraction | int | float | str
DEFAULT_FACTORS = (Decimal("0.90"), Decimal("0.32"), Decimal("0.15"))


@dataclass(frozen=True)
class FormulaPath:
    """A supplied reform path; defaults reproduce the unreformed formula.

    Every year-keyed mapping contains values for eligibility cohorts, not
    payment years. Entries are exact cohort values: a missing year fails rather
    than silently carrying forward an incompletely frozen scoring path.

    ``effective_year`` gates custom bend-point changes. ``factor_start_year``
    gates custom factors independently. With ``recompute_mode='cohort'`` these
    gates use eligibility; ``'retroactive'`` uses the supplied payment year and
    retains the original eligibility-year bend points. The S.770 preset always
    has the introduced bill's 2026 effective year. Its separately controllable
    bend-point increase implements the documented restricted-survivor reading;
    disabling that increase leaves the 95% first factor in place.
    """

    effective_year: int | None = None
    bend_point_multipliers: tuple[Number, Number] = (1, 1)
    factor_values: tuple[Number, Number, Number] | None = None
    factor_start_year: int | None = None
    full_price_indexing_start_year: int | None = None
    real_wage_scale_by_year: Mapping[int, Number] | None = None
    progressive_price_indexing_start_year: int | None = None
    bend_point_fraction: Number | None = None
    threshold_by_year: Mapping[int, Number] | None = None
    maximum_aime_by_year: Mapping[int, Number] | None = None
    maximum_pia_target_by_year: Mapping[int, Number] | None = None
    s770: bool = False
    s770_increase_first_bend_point: bool = True


@dataclass(frozen=True)
class PIAInverse:
    """AIME interval giving a supplied dime-rounded unreformed PIA.

    The interval is ``[exact_lower, exact_upper)``. ``lower`` and ``upper`` are
    convenient 50-digit Decimal representations, rounded toward +infinity.
    This preserves the lower-endpoint point convention under forward PIA
    truncation even when the rational endpoint has no finite decimal expansion.
    Use the exact Fraction fields for interval membership or exact endpoints.
    """

    lower: Decimal
    upper: Decimal
    exact_lower: Fraction
    exact_upper: Fraction


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


def _year(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer calendar year")
    if value < 1983:
        raise ValueError("PIA benchmark years before 1983 are unsupported")
    return value


def _scale(bend_points, factors):
    if len(bend_points) != 2 or len(factors) != 3:
        raise ValueError("PIA requires two bend points and three factors")
    bp1, bp2 = (_number(value, "bend point") for value in bend_points)
    rates = tuple(_number(value, "PIA factor") for value in factors)
    if not 0 < bp1 < bp2:
        raise ValueError("PIA bend points must satisfy 0 < first < second")
    if any(rate < 0 for rate in rates):
        raise ValueError("PIA factors must be nonnegative")
    return (bp1, bp2), rates


def _raw_pia(aime, bend_points, factors):
    bp1, bp2 = bend_points
    first, second, third = factors
    return (
        first * min(aime, bp1)
        + second * max(min(aime, bp2) - bp1, 0)
        + third * max(aime - bp2, 0)
    )


def _active(start_year, eligibility_year, payment_year, recompute_mode):
    if start_year is None:
        return True
    _year(start_year, "reform start year")
    year = eligibility_year if recompute_mode == "cohort" else payment_year
    return year >= start_year


def _computation_years(eligibility_year, payment_year, recompute_mode):
    year = _year(eligibility_year, "eligibility year")
    if recompute_mode not in ("cohort", "retroactive"):
        raise ValueError("recompute_mode must be 'cohort' or 'retroactive'")
    if payment_year is not None:
        _year(payment_year, "payment year")
        if payment_year < year:
            raise ValueError("payment year cannot precede eligibility year")
    if recompute_mode == "retroactive" and payment_year is None:
        raise ValueError("retroactive recomputation requires a payment year")
    return year


def _active_features(path, year, payment_year, recompute_mode):
    """Resolve provision gates once for calculation and inference decisions."""
    features = set()
    if _active(path.effective_year, year, payment_year, recompute_mode):
        features.add("bend_points")
    if path.factor_values is not None and _active(
        path.factor_start_year, year, payment_year, recompute_mode
    ):
        features.add("factors")
    if path.s770 and _active(2026, year, payment_year, recompute_mode):
        features.add("s770")
    for feature, start in (
        ("full_price_indexing", path.full_price_indexing_start_year),
        ("progressive_price_indexing", path.progressive_price_indexing_start_year),
    ):
        if start is not None and _active(start, year, payment_year, recompute_mode):
            features.add(feature)
    return features


def has_active_reform(
    formula_path: FormulaPath | None,
    eligibility_year: int,
    payment_year: int | None = None,
    recompute_mode: str = "cohort",
) -> bool:
    """Whether a provision applies and can require recovering supplied AIME.

    A configured future provision or identity custom scale must not make a
    supplied unreformed PIA go through an unnecessary inverse. Enabled indexing
    paths still require validation of their frozen inputs, including at an
    identity anchor.
    """
    year = _computation_years(eligibility_year, payment_year, recompute_mode)
    path = formula_path or FormulaPath()
    features = _active_features(path, year, payment_year, recompute_mode)
    if features & {"s770", "full_price_indexing", "progressive_price_indexing"}:
        return True
    if "bend_points" in features:
        if len(path.bend_point_multipliers) != 2:
            raise ValueError("two bend-point multipliers are required")
        if any(
            _number(value, "bend-point multiplier") != 1
            for value in path.bend_point_multipliers
        ):
            return True
    return "factors" in features and tuple(
        _number(value, "PIA factor") for value in path.factor_values
    ) != tuple(Fraction(value) for value in DEFAULT_FACTORS)


def _cohort_value(path, year, name):
    if path is None or year not in path:
        raise ValueError(f"{name} requires a frozen value for eligibility year {year}")
    return _number(path[year], name)


def _progressive_threshold(
    eligibility_year: int,
    formula_path: FormulaPath,
    *,
    bend_points: tuple[Number, Number],
) -> Fraction:
    year = _year(eligibility_year, "eligibility year")
    bends, _ = _scale(bend_points, DEFAULT_FACTORS)
    if formula_path.threshold_by_year is not None:
        threshold = _cohort_value(
            formula_path.threshold_by_year, year, "progressive dollar threshold"
        )
    elif formula_path.bend_point_fraction is not None:
        fraction = _number(formula_path.bend_point_fraction, "bend-point fraction")
        if not 0 <= fraction <= 1:
            raise ValueError("bend-point fraction must be between zero and one")
        threshold = bends[0] + fraction * (bends[1] - bends[0])
    else:
        raise ValueError(
            "Progressive price indexing requires a bend-point fraction or "
            "a supplied dollar threshold path"
        )
    if threshold < bends[0]:
        raise ValueError("progressive threshold cannot cut the protected first segment")
    return threshold


def progressive_threshold(
    eligibility_year: int,
    formula_path: FormulaPath,
    *,
    bend_points: tuple[Number, Number],
) -> Decimal:
    """Return the M8 protected threshold; a supplied dollar path takes priority.

    The fractional threshold uses the unreformed eligibility-year bend points,
    including when another provision changes the formula's bend points. The
    formula itself retains the exact rational threshold through final rounding.
    """
    return _decimal(
        _progressive_threshold(eligibility_year, formula_path, bend_points=bend_points)
    )


def compute_pia(
    aime: Number,
    eligibility_year: int,
    formula_path: FormulaPath | None = None,
    payment_year: int | None = None,
    recompute_mode: str = "cohort",
    *,
    bend_points: tuple[Number, Number],
    factors: tuple[Number, Number, Number] = DEFAULT_FACTORS,
    round_result: bool = True,
    exact_result: bool = False,
) -> Decimal | Fraction:
    """Compute a monthly PIA from supplied AIME and eligibility-year inputs.

    Direct household AIME inputs must be whole dollars (the household adapter
    validates this). Fractional AIME remains supported here for the documented
    inverse lower-endpoint convention and continuous reform sensitivities.
    ``round_result=False`` exposes the formula before statutory dime truncation.
    Also requesting ``exact_result=True`` returns its exact rational value for
    mini-PIA aggregation; this requires ``round_result=False``.
    """
    if exact_result and round_result:
        raise ValueError("exact_result requires round_result=False")
    year = _computation_years(eligibility_year, payment_year, recompute_mode)
    amount = _number(aime, "AIME")
    if amount < 0:
        raise ValueError("AIME must be nonnegative")
    baseline_bends, rates = _scale(bend_points, factors)
    bends = baseline_bends
    path = formula_path or FormulaPath()
    features = _active_features(path, year, payment_year, recompute_mode)
    if "bend_points" in features:
        if len(path.bend_point_multipliers) != 2:
            raise ValueError("two bend-point multipliers are required")
        multipliers = tuple(
            _number(value, "bend-point multiplier")
            for value in path.bend_point_multipliers
        )
        bends = tuple(bp * multiplier for bp, multiplier in zip(bends, multipliers))
    if "factors" in features:
        _, rates = _scale(baseline_bends, path.factor_values)
    if "s770" in features:
        rates = (Fraction(95, 100), rates[1], rates[2])
        if path.s770_increase_first_bend_point:
            bends = (bends[0] * Fraction(118, 100), bends[1])
    bends, rates = _scale(bends, rates)

    # Full price indexing scales every marginal factor by a pinned ratio of
    # price growth to wage growth, using the same documented cohort index basis.
    if "full_price_indexing" in features:
        scale = _cohort_value(path.real_wage_scale_by_year, year, "real-wage scale")
        if scale <= 0:
            raise ValueError("real-wage scale must be positive")
        rates = tuple(rate * scale for rate in rates)

    result = _raw_pia(amount, bends, rates)
    if "progressive_price_indexing" in features:
        threshold = _progressive_threshold(year, path, bend_points=baseline_bends)
        if threshold < bends[0]:
            raise ValueError(
                "progressive threshold cuts the final formula's first segment"
            )
        maximum = _cohort_value(path.maximum_aime_by_year, year, "maximum-career AIME")
        target = _cohort_value(
            path.maximum_pia_target_by_year, year, "maximum-career PIA target"
        )
        protected_pia = _raw_pia(threshold, bends, rates)
        maximum_pia = _raw_pia(maximum, bends, rates)
        if maximum <= threshold or maximum_pia <= protected_pia:
            raise ValueError(
                "maximum-career AIME must exceed the progressive threshold"
            )
        if not protected_pia <= target <= maximum_pia:
            raise ValueError(
                "progressive PIA target is outside the protected/maximum bounds"
            )
        multiplier = (target - protected_pia) / (maximum_pia - protected_pia)
        result = _raw_pia(min(amount, threshold), bends, rates) + multiplier * max(
            result - protected_pia, 0
        )
    if round_result:
        # Rational arithmetic keeps exact dime boundaries exact; binary floats
        # and finite Decimal approximations cannot accidentally lose one dime.
        return Decimal((result * 10).numerator // (result * 10).denominator) / 10
    return result if exact_result else _decimal(result)


def inverse_unrounded(
    pia: Number,
    eligibility_year: int,
    *,
    bend_points: tuple[Number, Number],
    factors: tuple[Number, Number, Number] = DEFAULT_FACTORS,
) -> Fraction:
    """Invert the fixed unreformed, unrounded historical PIA scale exactly."""
    _year(eligibility_year, "eligibility year")
    amount = _number(pia, "PIA")
    if amount < 0:
        raise ValueError("PIA must be nonnegative")
    bends, rates = _scale(bend_points, factors)
    if any(rate <= 0 for rate in rates):
        raise ValueError("baseline inverse requires three positive historical factors")
    bp1, bp2 = bends
    first, second, third = rates
    first_pia = first * bp1
    second_pia = first_pia + second * (bp2 - bp1)
    if amount <= first_pia:
        return amount / first
    if amount <= second_pia:
        return bp1 + (amount - first_pia) / second
    return bp2 + (amount - second_pia) / third


def inverse_pia(
    pia: Number,
    eligibility_year: int,
    *,
    bend_points: tuple[Number, Number],
    factors: tuple[Number, Number, Number] = DEFAULT_FACTORS,
) -> PIAInverse:
    """Invert an exact dime-rounded baseline PIA, never reform factors.

    An observed rounded paid benefit is a wider measurement interval and must
    first be propagated backward through its payment/claim/COLA operations.
    """
    amount = _number(pia, "PIA")
    if (amount * 10).denominator != 1:
        raise ValueError("an exact eligibility PIA must be a multiple of one dime")
    lower = inverse_unrounded(
        amount, eligibility_year, bend_points=bend_points, factors=factors
    )
    upper = inverse_unrounded(
        amount + Fraction(1, 10),
        eligibility_year,
        bend_points=bend_points,
        factors=factors,
    )
    return PIAInverse(
        lower=_decimal(lower, ceiling=True),
        upper=_decimal(upper, ceiling=True),
        exact_lower=lower,
        exact_upper=upper,
    )
