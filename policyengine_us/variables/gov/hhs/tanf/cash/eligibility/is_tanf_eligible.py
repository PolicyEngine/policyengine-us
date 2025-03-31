from policyengine_us.model_api import *


class is_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligibility for TANF"
    documentation = "Whether the family is eligible for Temporary Assistance for Needy Families benefit."

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        economic_eligible = where(
            spm_unit("is_tanf_enrolled", period),
            spm_unit("is_tanf_continuous_eligible", period),
            spm_unit("is_tanf_initial_eligible", period),
        )
        return demographic_eligible & economic_eligible
