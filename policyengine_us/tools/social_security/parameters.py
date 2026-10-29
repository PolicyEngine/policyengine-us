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


def _snapshot(node, year):
    # Snapshot only the requested SSA subtree; a root snapshot traverses the
    # entire US parameter tree even when the caller needs just two bend points.
    return node(f"{year}-01-01")


def _frozen_value(node, name, year):
    """Require a published January observation for this exact cohort.

    Core normally holds a scalar's last value forward. Frozen indexing paths
    instead enumerate every cohort explicitly; carrying an old scale, target
    or dollar threshold forward would manufacture an unfrozen reform path.
    """
    instant = f"{year}-01-01"
    return next(
        (
            entry.value
            for entry in getattr(node, name).values_list
            if entry.instant_str == instant
        ),
        None,
    )


def bend_points_at(parameters, eligibility_year):
    """Select initial-eligibility bends, with historical values before 2015.

    The separate historical table avoids changing the ordinary model's legacy
    scale. Future years use that scale's existing wage-indexed projections.
    """
    year = _year(eligibility_year)
    pia = _snapshot(parameters.gov.ssa.social_security.pia, year)
    if year <= 2026:
        return (pia.bend_points.first, pia.bend_points.second)
    return tuple(pia.formula_factors.thresholds[1:3])


def formula_path_at(parameters, eligibility_year, payment_year):
    """Return ``(FormulaPath, recompute_mode)`` for one worker and payment year.

    Cohort-only enablement, custom factors and bend multipliers read their
    dated values at eligibility and stay fixed for that cohort. Only an
    enabled payment-year explicit custom recompute reads the payment-year
    formula while keeping that worker's initial-eligibility bends. Frozen indexing
    scales, dollar thresholds, maximum-career AIMEs and targets require an
    explicit observation at January 1 of the eligibility year. A missing
    dollar override falls back to the supplied hold-forward bend-point
    fraction; other missing frozen data fail in the shared PIA service.

    S.770 has its own switch and mandatory older-beneficiary recomputation.
    Custom gates are resolved here so enabling S.770 cannot accidentally extend
    a separately configured cohort-only custom reform to older beneficiaries.
    """
    year = _year(eligibility_year)
    payment = _year(payment_year)
    if payment < year:
        raise ValueError("payment year cannot precede eligibility year")
    pia_node = parameters.gov.contrib.ssa.pia
    current = _snapshot(pia_node, payment)
    cohort = _snapshot(pia_node, year)
    custom_recompute = bool(current.in_effect and current.recompute_existing)
    enabled = current.in_effect if custom_recompute else cohort.in_effect
    selection_year = payment if custom_recompute else year
    settings = _snapshot(pia_node, selection_year)
    s770 = bool(
        _snapshot(parameters.gov.contrib.congress.s770.section_2, payment).in_effect
        and payment >= 2026
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
            scale = _frozen_value(pia_node.full_price_indexing, "real_wage_scale", year)
            values["full_price_indexing_start_year"] = int(full.start_year)
            values["real_wage_scale_by_year"] = None if scale is None else {year: scale}

        progressive = settings.progressive_price_indexing
        if progressive.in_effect and selection_year >= progressive.start_year:
            values["progressive_price_indexing_start_year"] = int(
                progressive.start_year
            )
            values["bend_point_fraction"] = _optional(
                progressive, "bend_point_fraction"
            )
            for parameter_name, field in (
                ("threshold", "threshold_by_year"),
                ("maximum_aime", "maximum_aime_by_year"),
                ("maximum_pia_target", "maximum_pia_target_by_year"),
            ):
                value = _frozen_value(
                    pia_node.progressive_price_indexing, parameter_name, year
                )
                values[field] = None if value is None else {year: value}

    mode = "retroactive" if custom_recompute or s770 else "cohort"
    return FormulaPath(**values), mode
