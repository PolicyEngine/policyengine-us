from policyengine_us.model_api import *


class sc_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SC TANF resources eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.tanf.eligibility.resource_limit
        size = spm_unit("spm_unit_size", period)
        resource_limit = p * size
        countable_resources = spm_unit("sc_tanf_countable_resources", period)
        return countable_resources <= resource_limit
