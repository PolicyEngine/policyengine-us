from policyengine_us.model_api import *


class sc_tanf_resource_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Carolina TANF resource eligible"
    definition_period = YEAR
    defined_for = StateCode.SC

    def formula(spm_unit, period, parameters):
        resource_limit = parameters(period).gov.states.sc.tanf.resources.limit
        countable_resources = add(
            spm_unit, period, ["sc_tanf_countable_resources"]
        )
        return countable_resources <= resource_limit
