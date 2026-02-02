from policyengine_us.model_api import *


class ia_fip_countable_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP countable income eligible"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf#page=20"

    def formula(spm_unit, period, parameters):
        # Test 3: Countable income < payment standard
        # Countable income applies both 20% deduction AND 58% work incentive disregard
        countable_income = spm_unit("ia_fip_countable_income", period)
        payment_standard = spm_unit("ia_fip_payment_standard", period)
        return countable_income < payment_standard
