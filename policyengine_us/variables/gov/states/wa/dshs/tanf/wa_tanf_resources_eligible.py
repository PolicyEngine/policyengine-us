from policyengine_us.model_api import *


class wa_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Washington TANF resources eligible"
    definition_period = YEAR
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wa.dshs.tanf.eligibility.resources
        countable_resources = spm_unit("wa_tanf_countable_resources", period)
        return countable_resources <= p.limit
