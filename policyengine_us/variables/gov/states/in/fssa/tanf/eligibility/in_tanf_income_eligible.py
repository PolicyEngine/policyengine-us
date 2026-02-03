from policyengine_us.model_api import *


class in_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana TANF income eligible"
    definition_period = MONTH
    reference = "https://iar.iga.in.gov/code/2026/470/10.3#470-10.3-4"  # 470 IAC 10.3-4
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # Indiana uses two income tests per 470 IAC 10.3-4:
        # 1. Countable income test (with eligibility disregards)
        # 2. Payment test (with payment disregards)
        # Must pass both tests for fiscal eligibility.
        countable_eligible = spm_unit(
            "in_tanf_countable_income_eligible", period
        )
        payment_eligible = spm_unit("in_tanf_payment_eligible", period)
        return countable_eligible & payment_eligible
