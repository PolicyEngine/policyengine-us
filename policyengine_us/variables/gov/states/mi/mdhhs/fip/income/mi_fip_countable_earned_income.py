from policyengine_us.model_api import *


class mi_fip_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan FIP countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/518.pdf",
        "https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Inside-MDHHS/Reports-and-Statistics---Human-Services/State-Plans-and-Federal-Regulations/TANF_State_Plan_2023.pdf",
    )
    defined_for = StateCode.MI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mi.mdhhs.fip

        # Get gross earned income for all SPM unit members
        # Use federal TANF gross earned income directly
        person = spm_unit.members
        gross_earned_income = person("tanf_gross_earned_income", period)
        total_gross_earned = spm_unit.sum(gross_earned_income)

        # Apply earned income deduction: $200 + 50% of remainder
        # Note: Using ongoing rate for simplified implementation
        # Full implementation would distinguish initial vs ongoing eligibility
        flat_deduction = (
            p.income.deductions.earned_income_disregard.flat_amount
        )
        percent_deduction = (
            p.income.deductions.earned_income_disregard.percent_of_remainder
        )

        remainder = max_(total_gross_earned - flat_deduction, 0)
        total_deduction = flat_deduction + (percent_deduction * remainder)

        return max_(total_gross_earned - total_deduction, 0)
