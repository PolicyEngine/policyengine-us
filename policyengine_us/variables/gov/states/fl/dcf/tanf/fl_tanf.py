from policyengine_us.model_api import *


class fl_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TANF"
    unit = USD
    definition_period = MONTH
    reference = "Florida Statute § 414.095(12)"
    documentation = (
        "Florida Temporary Cash Assistance (TCA) monthly benefit amount"
    )
    defined_for = "fl_tanf_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.dcf.tanf

        # Get payment standard and countable income
        payment_standard = spm_unit("fl_tanf_payment_standard", period)
        countable_income = spm_unit("fl_tanf_countable_income", period)
        family_cap_reduction = spm_unit("fl_tanf_family_cap_reduction", period)

        # Calculate benefit: payment standard - countable income - family cap reduction
        gross_benefit = (
            payment_standard - countable_income - family_cap_reduction
        )

        # Round down to nearest dollar (using int conversion)
        rounded_benefit = gross_benefit.astype(int)

        # Apply minimum benefit threshold
        minimum_benefit = p.minimum_benefit

        # If benefit is below minimum, no cash payment (return 0)
        final_benefit = where(
            rounded_benefit >= minimum_benefit, rounded_benefit, 0
        )

        return max_(final_benefit, 0)
