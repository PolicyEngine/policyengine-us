from policyengine_us.model_api import *


class nj_wfnj_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Jersey WFNJ resources eligible"
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-20"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.wfnj.eligibility.resources
        countable_resources = spm_unit(
            "nj_wfnj_countable_resources", period.this_year
        )
        return countable_resources <= p.limit
