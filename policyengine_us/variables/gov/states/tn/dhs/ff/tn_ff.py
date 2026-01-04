from policyengine_us.model_api import *


class tn_ff(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50-.20"
    defined_for = "tn_ff_eligible"

    def formula(spm_unit, period, parameters):
        # Tennessee Families First TANF benefit using fill-the-gap methodology.
        # The benefit equals the minimum of: (1) the payment standard (SPA or DGPA),
        # or (2) the deficit (Consolidated Need Standard minus countable income).
        # No payment is made if the calculated benefit is less than the minimum grant.
        # Get payment standard (SPA or DGPA based on eligibility)
        payment_standard = spm_unit("tn_ff_payment_standard", period)

        # Calculate countable income
        countable_income = spm_unit("tn_ff_countable_income", period)

        p = parameters(period).gov.states.tn.dhs.ff.payment
        unit_size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(unit_size, p.max_family_size)

        deficit = max_(
            p.consolidated_need_standard[capped_size] - countable_income, 0
        )
        calculated_benefit = min_(payment_standard, deficit)

        return where(
            calculated_benefit >= p.minimum_grant, calculated_benefit, 0
        )
