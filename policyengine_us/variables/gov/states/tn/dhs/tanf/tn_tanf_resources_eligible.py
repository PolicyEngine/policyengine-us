from policyengine_us.model_api import *


class tn_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Tennessee TANF resources eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50",
        "Tennessee Administrative Code § 1240-01-50 - Financial Eligibility Requirements",
        "Tennessee TANF State Plan 2024-2027",
    )
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        countable_resources = spm_unit("tn_tanf_countable_resources", period)
        p = parameters(period).gov.states.tn.dhs.tanf.resource_limit
        resource_limit = p.amount
        return countable_resources <= resource_limit
