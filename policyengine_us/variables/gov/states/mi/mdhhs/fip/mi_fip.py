from policyengine_us.model_api import *


class mi_fip(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan Family Independence Program"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/520.pdf#page=4",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/518.pdf#page=5",
    )
    defined_for = "mi_fip_eligible"

    def formula(spm_unit, period, parameters):
        # BEM 520 Section F: Issuance Amount
        # "Subtract line 2 and line 3 from the amount on line 1"
        # Line 1: Payment Standard (from Section B)
        # Line 2: Countable Income (from Section D - uses 50% deduction)
        # Line 3: Recoupment (simplified: excluded)

        payment_standard = spm_unit("mi_fip_payment_standard", period)
        countable_income = spm_unit(
            "mi_fip_countable_income_for_benefit", period
        )

        # BEM 518: Minimum benefit requirement is $10 deficit
        # Negative benefits are set to 0
        benefit = max_(payment_standard - countable_income, 0)
        return min_(benefit, payment_standard)
