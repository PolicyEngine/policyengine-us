"""Read eligibility-cohort parameters for the opt-in monthly PIA service."""

from policyengine_core.errors import ParameterNotFoundError

from .pia import FormulaPath


def _year(value):
    if isinstance(value, bool) or int(value) != value or value < 1983:
        raise ValueError(
            "PIA benchmark years before 1983 or noninteger years are unsupported"
        )
    return int(value)


def _optional(node, name):
    # Core omits a null parameter from ParameterNodeAtInstant._children and
    # raises ParameterNotFoundError on access. An unset fraction/threshold must
    # stay unset rather than becoming an implicit zero or population estimate.
    try:
        return getattr(node, name)
    except ParameterNotFoundError:
        return None


def _snapshot(parameters, year):
    return parameters(f"{year}-01-01")


def bend_points_at(parameters, eligibility_year):
    """Select initial-eligibility bends, with historical values before 2015.

    The separate historical table avoids changing the ordinary model's legacy
    scale. Future years use that scale's existing wage-indexed projections.
    """
    year = _year(eligibility_year)
    pia = _snapshot(parameters, year).gov.ssa.social_security.pia
    if year <= 2026:
        return (pia.bend_points.first, pia.bend_points.second)
    return tuple(pia.formula_factors.thresholds[1:3])


def formula_path_at(parameters, eligibility_year, payment_year):
    """Return ``(FormulaPath, recompute_mode)`` for one worker and payment year.

    Cohort-only custom factors and bend multipliers read their dated values at
    eligibility. An explicit custom recompute reads the payment-year formula
    while keeping that worker's initial-eligibility bends. Frozen indexing
    scales, thresholds, maximum-career AIMEs and targets always read at the
    eligibility year. Any missing frozen data fail in the shared PIA service.

    S.770 has its own switch and mandatory older-beneficiary recomputation.
    Custom gates are resolved here so enabling S.770 cannot accidentally extend
    a separately configured cohort-only custom reform to older beneficiaries.
    """
    year = _year(eligibility_year)
    payment = _year(payment_year)
    if payment < year:
        raise ValueError("payment year cannot precede eligibility year")
    current = _snapshot(parameters, payment)
    enabled = current.gov.contrib.ssa.pia.in_effect
    custom_recompute = bool(enabled and current.gov.contrib.ssa.pia.recompute_existing)
    selection_year = payment if custom_recompute else year
    settings = _snapshot(parameters, selection_year).gov.contrib.ssa.pia
    cohort = _snapshot(parameters, year).gov.contrib.ssa.pia
    s770 = bool(
        current.gov.contrib.congress.s770.section_2.in_effect and payment >= 2026
    )

    values = {"s770": s770}
    if enabled:
        if selection_year >= settings.effective_year:
            values["bend_point_multipliers"] = (
                settings.bend_point_multipliers.first,
                settings.bend_point_multipliers.second,
            )
        if selection_year >= settings.factors.start_year:
            values["factor_values"] = (
                settings.factors.first,
                settings.factors.second,
                settings.factors.third,
            )

        full = settings.full_price_indexing
        if full.in_effect and selection_year >= full.start_year:
            scale = _optional(cohort.full_price_indexing, "real_wage_scale")
            values["full_price_indexing_start_year"] = int(full.start_year)
            values["real_wage_scale_by_year"] = None if scale is None else {year: scale}

        progressive = settings.progressive_price_indexing
        if progressive.in_effect and selection_year >= progressive.start_year:
            frozen = cohort.progressive_price_indexing
            values["progressive_price_indexing_start_year"] = int(
                progressive.start_year
            )
            values["bend_point_fraction"] = _optional(frozen, "bend_point_fraction")
            for parameter_name, field in (
                ("threshold", "threshold_by_year"),
                ("maximum_aime", "maximum_aime_by_year"),
                ("maximum_pia_target", "maximum_pia_target_by_year"),
            ):
                value = _optional(frozen, parameter_name)
                values[field] = None if value is None else {year: value}

    mode = "retroactive" if custom_recompute or s770 else "cohort"
    return FormulaPath(**values), mode
