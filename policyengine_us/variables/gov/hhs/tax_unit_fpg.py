from policyengine_us.model_api import *


class tax_unit_fpg(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit's federal poverty guideline"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        n = tax_unit("tax_unit_size", period)
        state_group = tax_unit.household("state_group_str", period)
        p_fpg = parameters(period).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        return p1 + pn * (n - 1)
