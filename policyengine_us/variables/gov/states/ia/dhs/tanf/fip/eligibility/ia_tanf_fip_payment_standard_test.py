from policyengine_us.model_api import *


class ia_tanf_fip_payment_standard_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP Payment Standard test"
    definition_period = MONTH
    reference = "Iowa Administrative Code 441-41.28"
    documentation = (
        "Families pass this test if countable net income is below the "
        "payment standard for their family size. Passing qualifies them "
        "for a positive FIP benefit."
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        # Get countable net income (after all deductions)
        countable_net = spm_unit("ia_tanf_fip_countable_net_income", period)

        # Get payment standard (Schedule of Basic Needs)
        payment_standard = spm_unit("ia_tanf_fip_payment_standard", period)

        # Pass if countable net income is below payment standard
        return countable_net < payment_standard
