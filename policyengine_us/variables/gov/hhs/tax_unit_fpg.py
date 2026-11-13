from policyengine_us.model_api import *
from policyengine_core.periods import instant


def fpg(unit_size, state_group, period, parameters, year_lag=0):
    """Return the annual guideline for the supplied size and guideline year.

    Lag only the parameter date, preserving its month and day. Callers supply
    the current household size and apply any caps, policy rates, or rounding.
    The 2016 guideline year uses HHS's nonuniform household-size table.
    """
    guideline_date = instant(period).offset(-int(year_lag), "year")
    p_fpg = parameters(guideline_date).gov.hhs.fpg
    p1 = p_fpg.first_person[state_group]
    pn = p_fpg.additional_person[state_group]
    linear_guideline = p1 + pn * (unit_size - 1)
    table = parameters(guideline_date).gov.hhs.fpg_table
    if not table.in_effect:
        return linear_guideline

    # Some callers supply a scalar size for a vector of households. Core's
    # table lookup needs one size per result, including a one-element vector
    # when both the size and geography are scalars.
    table_size, table_geography, _ = np.broadcast_arrays(
        unit_size, state_group, np.atleast_1d(linear_guideline)
    )
    source_geographies = list(table.amount)
    has_table = np.isin(table_geography, source_geographies)
    safe_geography = where(has_table, table_geography, source_geographies[0])
    # HHS retained some prior-year amounts in 2016, so the published
    # additional-person amount applies only beyond the last listed size.
    # Keep the legacy result for inputs outside the integer-size domain.
    valid_size = (
        np.isfinite(table_size)
        & (table_size >= table.min_household_size)
        & (table_size == np.floor(table_size))
    )
    lookup_size = min_(
        where(valid_size, table_size, table.min_household_size),
        table.max_household_size,
    ).astype(int)
    listed_guideline = table.amount[safe_geography][lookup_size]
    extended_guideline = listed_guideline + pn * max_(
        table_size - table.max_household_size, 0
    )
    # HHS does not define territory guidelines. Preserve their existing
    # placeholders rather than applying one of the three source tables.
    result = where(has_table & valid_size, extended_guideline, linear_guideline)
    return result.item() if np.ndim(linear_guideline) == 0 else result


class tax_unit_fpg(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit's federal poverty guideline"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        n = tax_unit("tax_unit_size", period)
        state_group = tax_unit.household("state_group_str", period)
        return fpg(n, state_group, period, parameters)
