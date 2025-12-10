from policyengine_us.model_api import *


class or_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oregon TANF eligible"
    definition_period = MONTH
    reference = "https://oregon.public.law/rules/oar_461-135-0070"
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        has_citizen = spm_unit.any(
            person("is_citizen_or_legal_immigrant", period)
        )
        income_eligible = spm_unit("or_tanf_income_eligible", period)
        resources_eligible = spm_unit("or_tanf_resources_eligible", period)
        return (
            demographic_eligible
            & has_citizen
            & income_eligible
            & resources_eligible
        )
