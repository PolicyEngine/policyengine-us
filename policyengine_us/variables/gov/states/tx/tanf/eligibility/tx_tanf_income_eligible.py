from policyengine_us.model_api import *


class tx_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Texas TANF income test"
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Texas TANF has two income eligibility tests:
        # Part A: Budgetary needs test (income ≤ budgetary needs amount)
        # Part B: Recognizable needs test (income ≤ recognizable needs amount)
        #
        # Test requirements by enrollment status:
        # - New applicants (not enrolled): Must pass Part A AND Part B
        # - Continuing recipients (enrolled): Must pass Part B only

        is_enrolled = spm_unit("is_tanf_enrolled", period)
        passes_budgetary = spm_unit("tx_tanf_budgetary_needs_test", period)
        passes_recognizable = spm_unit(
            "tx_tanf_recognizable_needs_test", period
        )

        # Apply the appropriate test(s) based on enrollment status
        return where(
            is_enrolled,
            passes_recognizable,  # Continuing: Part B only
            passes_budgetary
            & passes_recognizable,  # Applicants: Part A AND Part B
        )
