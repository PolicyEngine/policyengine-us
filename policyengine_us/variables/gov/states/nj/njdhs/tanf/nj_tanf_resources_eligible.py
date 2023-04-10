from policyengine_us.model_api import *


class nj_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Jersey TANF resources eligible"
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.tanf.eligibility.resources
        countable_resources = spm_unit("nj_tanf_countable_resources", period)
        return countable_resources <= p.resource_limit
