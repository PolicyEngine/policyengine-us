from policyengine_us.model_api import *


class mi_fip_countable_earned_income_for_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan FIP countable earned income for benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/518.pdf",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/520.pdf",
    )
    defined_for = StateCode.MI

    # BEM 518: "Apply this disregard separately to each program group member's
    # earned income"
    # Sum the per-person countable earned income across all household members
    adds = ["mi_fip_earned_income_after_deductions_for_benefit_person"]
