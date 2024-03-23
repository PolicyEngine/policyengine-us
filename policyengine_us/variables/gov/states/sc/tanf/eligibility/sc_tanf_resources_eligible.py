from policyengine_us.model_api import *


class sc_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Carolina TANF resources eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC

    def formula(spm_unit, period, parameters):
        resource_limit = parameters(
            period
        ).gov.states.sc.tanf.eligibility.resource_limit
        countable_resources = add(spm_unit, period, ["sc_tanf_countable_resources"])
        return countable_resources <= resource_limit
