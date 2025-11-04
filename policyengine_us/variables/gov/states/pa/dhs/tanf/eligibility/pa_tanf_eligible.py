from policyengine_us.model_api import *


class pa_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF eligibility"
    documentation = "Pennsylvania TANF eligibility requires meeting demographic, income, and resource requirements."
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapters 145, 153, 175, 178, 183"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Must meet demographic requirements (age, deprivation)
        # Use federal demographic eligibility directly
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Must have at least one citizen or legal immigrant
        # Use federal immigration eligibility directly
        has_citizen = spm_unit.any(
            person("is_citizen_or_legal_immigrant", period)
        )

        # Must meet income requirements (countable income < FSA)
        income_eligible = spm_unit("pa_tanf_income_eligible", period)

        # Must meet resource requirements (assets <= $1,000)
        resource_eligible = spm_unit("pa_tanf_resource_eligible", period)

        # All requirements must be met
        return (
            demographic_eligible
            & has_citizen
            & income_eligible
            & resource_eligible
        )
