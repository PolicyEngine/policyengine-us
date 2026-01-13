from policyengine_us.model_api import *


class ia_tanf_fip(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa Family Investment Program (FIP/TANF)"
    unit = USD
    definition_period = MONTH
    reference = "Iowa Code Chapter 239B"
    documentation = (
        "https://hhs.iowa.gov/assistance-programs/cash-assistance/fip-tanf"
    )
    defined_for = "ia_tanf_fip_eligible"

    def formula(spm_unit, period, parameters):
        # Get payment standard for family size
        payment_standard = spm_unit("ia_tanf_fip_payment_standard", period)

        # Get countable net income (after all deductions)
        countable_net = spm_unit("ia_tanf_fip_countable_net_income", period)

        # Benefit = Payment Standard - Countable Net Income
        benefit = payment_standard - countable_net

        return max_(benefit, 0)
