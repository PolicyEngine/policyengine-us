from policyengine_us.model_api import *


class nm_works_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Mexico Works resources eligible"
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0510.html"
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.nm_works.resources.limit
        liquid_resources = spm_unit("nm_works_countable_liquid_resources", period)
        non_liquid_resources = spm_unit(
            "nm_works_countable_non_liquid_resources", period
        )
        return (liquid_resources <= p.liquid) & (non_liquid_resources <= p.non_liquid)
