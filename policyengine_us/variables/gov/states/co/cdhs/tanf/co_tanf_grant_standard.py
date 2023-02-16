from policyengine_us.model_api import *


class co_tanf_grant_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "CO TANF grant standard"
    unit = USD
    definition_period = YEAR
    defined_for = "co_tanf_eligible"

    def formula(spm_unit, period, parameters):
        people = spm_unit("spm_unit_size", period)
        adults = spm_unit("spm_unit_count_adults", period)
        children = people - adults
        p = parameters(period).gov.states.co.cdhs.tanf.grant_standard
        capped_children = min_(children, 10).astype(int)
        capped_adults = min_(adults, 2).astype(int)
        additional_children = children - capped_children
        base = p.main[capped_adults][capped_children]
        additional_grant_standard = p.additional_child * additional_children
        monthly = base + additional_grant_standard
        return monthly * MONTHS_IN_YEAR
