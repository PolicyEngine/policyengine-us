from policyengine_us.model_api import *


class mi_fip_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Michigan FIP based on income"
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/518.pdf",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/520.pdf",
    )
    defined_for = StateCode.MI

    def formula(spm_unit, period, parameters):
        # BEM 518 Page 1-2: Financial need exists when the group passes
        # the Qualifying Deficit Test (initial) or Issuance Deficit Test (ongoing)

        # BEM 520: "Bridges compares budgetable income... to the certified
        # group's payment standard for the benefit month"

        countable_income = spm_unit("mi_fip_countable_income", period)
        payment_standard = spm_unit("mi_fip_payment_standard", period)

        # Eligible if countable income is less than payment standard
        # Note: The countable_income variable already applies correct deduction
        # rates (20% for new applicants, 50% for enrolled) via the per-person
        # deduction variable based on is_tanf_enrolled status
        return countable_income < payment_standard
