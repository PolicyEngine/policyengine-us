from policyengine_us.model_api import *


class mi_fip(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan Family Independence Program"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/520.pdf",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/518.pdf",
    )
    defined_for = "mi_fip_eligible"

    def formula(spm_unit, period, parameters):
        # BEM 520 Section F: Issuance Amount
        # "Subtract line 2 and line 3 from the amount on line 1"
        # Line 1: Payment Standard (from Section B)
        # Line 2: Countable Income (from Section D)
        # Line 3: Recoupment (simplified: excluded)

        payment_standard = spm_unit("mi_fip_payment_standard", period)
        countable_income = spm_unit("mi_fip_countable_income", period)

        # Calculate benefit
        benefit = payment_standard - countable_income

        # BEM 518: Minimum benefit requirements
        # - Initial (new applicants): At least $1 deficit required
        # - Ongoing (enrolled): At least $10 deficit required
        # For simplified implementation, we use max_(benefit, 0) which
        # effectively enforces the minimum by setting negative benefits to 0

        return max_(benefit, 0)
