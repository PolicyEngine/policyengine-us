from policyengine_us.model_api import *


class nj_wfnj_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey WFNJ maximum benefit"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-3"
    )

    def formula(spm_unit, period, parameters):
        people = spm_unit("spm_unit_size", period.this_year)
        p = parameters(period).gov.states.nj.njdhs.wfnj
        capped_people = min_(people, p.max_household_size).astype(int)
        additional_people = people - capped_people
        base = p.maximum_benefit.main[capped_people]
        additional = p.maximum_benefit.additional * additional_people
        return base + additional
