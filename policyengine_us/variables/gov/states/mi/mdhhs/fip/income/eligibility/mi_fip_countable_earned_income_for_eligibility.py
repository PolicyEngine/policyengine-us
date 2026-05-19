from policyengine_us.model_api import *


class mi_fip_countable_earned_income_for_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan FIP countable earned income for eligibility"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/518.pdf",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/520.pdf",
    )
    defined_for = StateCode.MI

    # BEM 518: "Apply this disregard separately to each program group member's
    # earned income"
    # BEM 520 Section C: Qualifying Income Test (uses 20% rate for new applicants)
    # Sum the per-person initial deductions across all household members
    adds = ["mi_fip_earned_income_after_deductions_for_eligibility_person"]
