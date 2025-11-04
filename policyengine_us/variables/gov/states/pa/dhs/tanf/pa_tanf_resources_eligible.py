from policyengine_us.model_api import *


class pa_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF meets resource limit"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapter 183; Pennsylvania TANF Resource Limits"
    documentation = "The SPM unit's countable resources are at or below Pennsylvania's TANF resource limit. https://www.pa.gov/agencies/dhs/resources/cash-assistance/tanf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf
        resources = spm_unit("pa_tanf_countable_resources", period)
        resource_limit = p.resource_limit

        return resources <= resource_limit
