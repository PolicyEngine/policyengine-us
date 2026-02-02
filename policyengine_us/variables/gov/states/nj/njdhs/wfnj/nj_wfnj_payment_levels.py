from policyengine_us.model_api import *


class nj_wfnj_payment_levels(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey WFNJ payment levels"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-3"
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period.this_year)
        p = parameters(period).gov.states.nj.njdhs.wfnj
        capped_size = min_(size, p.max_household_size)
        additional = size - capped_size
        base = p.payment_levels.amount[capped_size]
        additional_amount = p.payment_levels.additional_person * additional
        return base + additional_amount
