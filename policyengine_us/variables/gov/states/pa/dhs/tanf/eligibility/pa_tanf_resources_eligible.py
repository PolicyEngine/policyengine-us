from policyengine_us.model_api import *


class pa_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Pennsylvania TANF resource limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf
        resources = spm_unit("pa_tanf_countable_resources", period)
        return resources <= p.resource_limit
