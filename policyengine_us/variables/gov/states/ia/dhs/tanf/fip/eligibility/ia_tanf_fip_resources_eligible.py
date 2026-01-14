from policyengine_us.model_api import *


class ia_tanf_fip_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP resources eligible"
    definition_period = MONTH
    reference = "Iowa Administrative Code 441-41.26"
    documentation = (
        "Families are resource eligible if resources are at or "
        "below the applicable limit."
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        assets = spm_unit("spm_unit_assets", period.this_year)
        resource_limit = spm_unit("ia_tanf_fip_resource_limit", period)

        return assets <= resource_limit
