from policyengine_us.model_api import *


class mi_fip_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan FIP countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/520.pdf",
        "https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Inside-MDHHS/Reports-and-Statistics---Human-Services/State-Plans-and-Federal-Regulations/TANF_State_Plan_2023.pdf",
    )
    defined_for = StateCode.MI

    def formula(spm_unit, period, parameters):
        # Countable income is the sum of:
        # 1. Countable earned income (after disregards)
        # 2. Gross unearned income (no disregard for unearned)
        countable_earned = spm_unit("mi_fip_countable_earned_income", period)

        # Use federal TANF gross unearned income directly
        person = spm_unit.members
        gross_unearned = person("tanf_gross_unearned_income", period)
        total_unearned = spm_unit.sum(gross_unearned)

        return countable_earned + total_unearned
