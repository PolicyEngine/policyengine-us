from policyengine_us.model_api import *


class ia_tanf_fip_eligible(Variable):
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
        non_financial_eligible = spm_unit(
            "ia_tanf_fip_non_financial_eligible", period
        )
        income_eligible = spm_unit("ia_tanf_fip_income_eligible", period)
        resources_eligible = spm_unit("ia_tanf_fip_resources_eligible", period)

        return non_financial_eligible & income_eligible & resources_eligible
