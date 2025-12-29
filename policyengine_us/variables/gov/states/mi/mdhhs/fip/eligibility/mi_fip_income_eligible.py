from policyengine_us.model_api import *


class mi_fip_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Michigan FIP based on income"
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/518.pdf#page=5",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/520.pdf#page=3",
    )
    defined_for = StateCode.MI

    def formula(spm_unit, period, parameters):
        # BEM 518 Page 3: Financial need exists when the group passes
        # the Qualifying Deficit Test (initial) or Issuance Deficit Test (ongoing)

        enrolled = spm_unit("is_tanf_enrolled", period)
        payment_standard = spm_unit("mi_fip_payment_standard", period)

        # New applicants: Use Qualifying Deficit Test (BEM 520 Section C)
        # - Uses 20% deduction rate
        countable_income_for_eligibility = spm_unit(
            "mi_fip_countable_income_for_eligibility", period
        )
        passes_qualifying_test = (
            countable_income_for_eligibility < payment_standard
        )

        # Enrolled recipients: Use Issuance Deficit Test (BEM 520 Section D)
        # - Uses 50% deduction rate (more generous)
        countable_income_for_benefit = spm_unit(
            "mi_fip_countable_income_for_benefit", period
        )
        passes_issuance_test = countable_income_for_benefit < payment_standard

        # Return appropriate test based on enrollment status
        return where(enrolled, passes_issuance_test, passes_qualifying_test)
