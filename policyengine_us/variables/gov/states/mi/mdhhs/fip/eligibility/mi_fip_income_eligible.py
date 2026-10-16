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
        # BEM 518: Financial need exists when the group passes the Issuance
        # Deficit Test and, at application, the Qualifying Deficit Test.
        p = parameters(period).gov.states.mi.mdhhs.fip
        enrolled = spm_unit("is_tanf_enrolled", period)
        payment_standard = spm_unit("mi_fip_payment_standard", period)

        # New applicants: Use Qualifying Deficit Test (BEM 520 Section C)
        # - Uses 20% deduction rate
        countable_income_for_eligibility = spm_unit(
            "mi_fip_countable_income_for_eligibility", period
        )
        passes_qualifying_test = countable_income_for_eligibility < payment_standard

        # All groups: Issuance Deficit Test (BEM 520 Section D)
        # - Uses 50% deduction rate (more generous)
        # - BEM 518: the deficit must be at least $10
        countable_income_for_benefit = spm_unit(
            "mi_fip_countable_income_for_benefit", period
        )
        issuance_deficit = payment_standard - countable_income_for_benefit
        passes_issuance_test = issuance_deficit >= p.minimum_payment

        # Applicants must pass both tests; enrolled recipients only the
        # Issuance Deficit Test.
        return passes_issuance_test & (enrolled | passes_qualifying_test)
