from policyengine_us.model_api import *


class or_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oregon TANF resources eligible"
    definition_period = YEAR
    reference = "https://oregon.public.law/rules/oar_461-160-0015"
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].odhs.tanf.resources
        countable_resources = spm_unit("or_tanf_countable_resources", period)
        return countable_resources <= p.limit
