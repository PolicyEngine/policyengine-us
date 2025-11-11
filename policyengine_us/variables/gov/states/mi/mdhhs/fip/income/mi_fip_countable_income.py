from policyengine_us.model_api import *


class mi_fip_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan FIP countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/520.pdf",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/520.pdf",
    )
    defined_for = StateCode.MI

    def formula(spm_unit, period, parameters):
        # BEM 520 Section D Line 9: "Enter the sum of line 7 and line 8"
        # Line 7: Countable earned income (after deductions per person)
        # Line 8: All countable unearned income

        # Countable earned income (aggregates per-person deductions)
        countable_earned = spm_unit("mi_fip_countable_earned_income", period)

        # Gross unearned income (no deductions for FIP per BEM 503)
        # Use federal TANF baseline
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])

        return countable_earned + gross_unearned
