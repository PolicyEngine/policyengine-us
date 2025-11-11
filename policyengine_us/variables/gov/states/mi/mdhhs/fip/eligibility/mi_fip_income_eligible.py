from policyengine_us.model_api import *


class mi_fip_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Michigan FIP based on income"
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/518.pdf",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/520.pdf",
        "https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Inside-MDHHS/Reports-and-Statistics---Human-Services/State-Plans-and-Federal-Regulations/TANF_State_Plan_2023.pdf",
    )
    defined_for = StateCode.MI

    def formula(spm_unit, period, parameters):
        # For simplified implementation, income eligibility is based on
        # whether the household would receive a positive benefit amount
        # Full implementation would use initial eligibility rules with 20% disregard

        countable_income = spm_unit("mi_fip_countable_income", period)
        payment_standard = spm_unit("mi_fip_payment_standard", period)

        # Eligible if countable income is less than payment standard
        return countable_income < payment_standard
