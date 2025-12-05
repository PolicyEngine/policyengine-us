from policyengine_us.model_api import *


class mi_fip_countable_income_for_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan FIP countable income for eligibility"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/520.pdf",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/503.pdf",
    )
    defined_for = StateCode.MI

    # BEM 520 Section C: Qualifying Income Test
    # Line C9: "Enter the sum of line 7 and line 8"
    # Line 7: Countable earned income (20% rate for initial eligibility)
    # Line 8: All countable unearned income (gross, no deductions per BEM 503)
    adds = [
        "mi_fip_countable_earned_income_for_eligibility",
        "tanf_gross_unearned_income",
    ]
