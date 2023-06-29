from policyengine_us.model_api import *


class pa_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF resources eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA

    def formula(spm_unit, period, parameters):
        resource_limit = parameters(
            period
        ).gov.states.pa.dhs.tanf.resource_limit
        total_assets = spm_unit("pa_tanf_countable_resources", period)
        return (
            spm_unit("pa_tanf_countable_resources", period) <= resource_limit
        )
