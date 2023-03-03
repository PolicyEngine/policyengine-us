from policyengine_us.model_api import *


class co_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "CO TANF income eligible"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        children = spm_unit("spm_unit_count_children", period)
        adults = spm_unit("spm_unit_count_adults", period)
        income = spm_unit("co_tanf_gross_countable_income", period)
        p = parameters(period).gov.states.co.cdhs.tanf.need_standard
        capped_children = min_(children, 10).astype(int)
        capped_adults = min_(adults, 2).astype(int)
        additional_children = children - capped_children
        base = p.main[capped_adults][capped_children]
        additional_need_standard = p.additional_child * additional_children
        need_standard = base + additional_need_standard
        return income < need_standard
        return eligible
