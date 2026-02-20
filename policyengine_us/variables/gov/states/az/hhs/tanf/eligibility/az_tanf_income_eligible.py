from policyengine_us.model_api import *


class az_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arizona TANF income eligible"
    definition_period = MONTH
    reference = "https://www.azleg.gov/ars/46/00292.htm"
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("az_tanf_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        payment_standard = spm_unit("az_tanf_payment_standard", period)

        # Test 1: Needy family test (income <= FPG rate * FPG)
        fpg_rate = spm_unit("az_tanf_fpg_rate", period)
        needy_family_test = countable_income <= fpg_rate * fpg

        # Test 2: Payment standard test (income <= payment standard)
        payment_standard_test = countable_income <= payment_standard

        return needy_family_test & payment_standard_test
