from policyengine_us.model_api import *


class oh_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Ohio TANF income eligibility"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5107.10",
        "http://codes.ohio.gov/oac/5101:1-23-20",
    )

    def formula(spm_unit, period, parameters):
        # Get countable income (after all disregards)
        countable_income = spm_unit("oh_tanf_countable_income", period)

        # Get payment standard for assistance group size
        payment_standard = spm_unit("oh_tanf_payment_standard", period)

        # Per OAC 5101:1-23-20 and ORC 5107.10(D):
        # Countable income must remain below the payment standard
        return countable_income < payment_standard
