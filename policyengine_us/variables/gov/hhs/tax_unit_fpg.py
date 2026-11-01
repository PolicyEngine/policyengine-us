from policyengine_us.model_api import *
from policyengine_core.periods import instant


def fpg(unit_size, state_group, period, parameters, year_lag=0):
    """Return the annual guideline for the supplied size and guideline year.

    Lag only the parameter date, preserving its month and day. Callers supply
    the current household size and apply any caps, policy rates, or rounding.
    """
    guideline_date = instant(period).offset(-int(year_lag), "year")
    p_fpg = parameters(guideline_date).gov.hhs.fpg
    p1 = p_fpg.first_person[state_group]
    pn = p_fpg.additional_person[state_group]
    return p1 + pn * (unit_size - 1)


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
