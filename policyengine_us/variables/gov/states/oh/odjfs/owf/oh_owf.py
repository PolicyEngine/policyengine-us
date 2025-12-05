from policyengine_us.model_api import *


class oh_owf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Ohio OWF"
    unit = USD
    definition_period = MONTH
    defined_for = "oh_owf_eligible"
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5101:1-23-40"
    )

    def formula(spm_unit, period, parameters):
        # Get payment standard for assistance group size
        payment_standard = spm_unit("oh_owf_payment_standard", period)

        # Get countable income (after all disregards)
        countable_income = spm_unit("oh_owf_countable_income", period)

        # Per OAC 5101:1-23-40: benefit = payment standard - countable income
        return max_(payment_standard - countable_income, 0)
