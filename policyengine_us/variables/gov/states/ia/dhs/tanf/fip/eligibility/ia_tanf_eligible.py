from policyengine_us.model_api import *


class ia_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP eligible"
    definition_period = MONTH
    reference = "Iowa Code Chapter 239B"
    documentation = (
        "Families are eligible for Iowa FIP if they meet non-financial, "
        "income, and resource requirements."
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        has_eligible_child = spm_unit("ia_tanf_fip_has_eligible_child", period)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        income_eligible = spm_unit("ia_tanf_fip_income_eligible", period)
        resources_eligible = spm_unit("ia_tanf_fip_resources_eligible", period)

        return (
            has_eligible_child
            & demographic_eligible
            & immigration_eligible
            & income_eligible 
            & resources_eligible
        )
