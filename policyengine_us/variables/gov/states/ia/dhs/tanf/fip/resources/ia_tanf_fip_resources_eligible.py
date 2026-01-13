from policyengine_us.model_api import *


class ia_tanf_fip_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP resources eligible"
    definition_period = MONTH
    reference = "Iowa Administrative Code 441-41.26"
    documentation = (
        "Families are resource eligible if countable resources are at or "
        "below the applicable limit."
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        countable_resources = spm_unit(
            "ia_tanf_fip_countable_resources", period
        )
        resource_limit = spm_unit("ia_tanf_fip_resource_limit", period)

        return countable_resources <= resource_limit
