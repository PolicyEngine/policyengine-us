from policyengine_us.model_api import *


class nj_wfnj_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey WFNJ maximum benefit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(spm_unit, period, parameters):
        people = spm_unit("spm_unit_size", period)
        capped_people = min_(people, 8).astype(int)
        additional_people = people - capped_people
        p = parameters(period).gov.states.nj.njdhs.wfnj.maximum_benefit
        base = p.main[capped_people]
        additional_maximum_benefit = p.additional * additional_people
        monthly = base + additional_maximum_benefit
        return monthly * MONTHS_IN_YEAR
