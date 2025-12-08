from policyengine_us.model_api import *


class pa_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF eligibility"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = (
        "https://www.pa.gov/agencies/dhs/resources/cash-assistance/tanf"
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        has_citizen = spm_unit.any(
            person("is_citizen_or_legal_immigrant", period)
        )
        income_eligible = spm_unit("pa_tanf_income_eligible", period)
        resources_eligible = spm_unit("pa_tanf_resources_eligible", period)

        return (
            demographic_eligible
            & has_citizen
            & income_eligible
            & resources_eligible
        )
