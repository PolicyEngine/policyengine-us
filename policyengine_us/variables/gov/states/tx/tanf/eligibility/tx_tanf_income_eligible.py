from policyengine_us.model_api import *


class tx_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Texas TANF income test"
    definition_period = MONTH
    reference = "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Must pass both budgetary needs test and recognizable needs test
        passes_budgetary = spm_unit("tx_tanf_budgetary_needs_test", period)
        passes_recognizable = spm_unit(
            "tx_tanf_recognizable_needs_test", period
        )

        # Both tests must pass for income eligibility
        return passes_budgetary & passes_recognizable
