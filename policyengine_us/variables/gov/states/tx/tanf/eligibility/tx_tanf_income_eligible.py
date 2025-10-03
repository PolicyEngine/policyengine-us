from policyengine_us.model_api import *


class tx_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Texas TANF income test"
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Texas TANF has two income eligibility tests per § 372.408:
        #
        # Budgetary needs test (§ 372.408 (a)(1)):
        #   - Uses income WITHOUT earned income disregards (1/3 or 90%)
        #   - Income < budgetary needs amount (100% of needs)
        #   - Applies to: NEW applicants only
        #
        # Recognizable needs test (§ 372.408 (a)(2)):
        #   - Uses income WITH earned income disregards (1/3 or 90%)
        #   - Income < recognizable needs amount (25% of budgetary needs)
        #   - Applies to: EVERYONE (applicants AND continuing recipients)
        #
        # Test requirements by enrollment status:
        # - New applicants: Must pass budgetary test AND recognizable test
        # - Continuing recipients: Must pass recognizable test only

        is_enrolled = spm_unit("is_tanf_enrolled", period)
        passes_budgetary = spm_unit("tx_tanf_budgetary_needs_test", period)
        passes_recognizable = spm_unit(
            "tx_tanf_recognizable_needs_test", period
        )

        # Apply the appropriate test(s) based on enrollment status
        return where(
            is_enrolled,
            passes_recognizable,  # Continuing: recognizable test only
            passes_budgetary & passes_recognizable,  # Applicants: BOTH tests
        )
