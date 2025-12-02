from policyengine_us.model_api import *


class mi_fip_countable_income_for_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan FIP countable income for benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/520.pdf",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/503.pdf",
    )
    defined_for = StateCode.MI

    # BEM 520 Section D Line 9: "Enter the sum of line 7 and line 8"
    # Line 7: Countable earned income (after per-person deductions)
    # Line 8: All countable unearned income (gross, no deductions per BEM 503)
    adds = [
        "mi_fip_countable_earned_income_for_benefit",
        "tanf_gross_unearned_income",
    ]
