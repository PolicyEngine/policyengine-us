from policyengine_us.model_api import *


class pa_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF eligibility"
    documentation = "Pennsylvania TANF eligibility requires meeting demographic, income, and resource requirements."
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapters 145, 153, 175, 178, 183"

    def formula(spm_unit, period, parameters):
        # Must meet demographic requirements (age, deprivation)
        demographic_eligible = spm_unit("pa_tanf_demographic_eligible", period)

        # Must meet income requirements (countable income < FSA)
        income_eligible = spm_unit("pa_tanf_income_eligible", period)

        # Must meet resource requirements (assets <= $1,000)
        resource_eligible = spm_unit("pa_tanf_resource_eligible", period)

        # All three requirements must be met
        return demographic_eligible & income_eligible & resource_eligible
