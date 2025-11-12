from policyengine_us.model_api import *


class tn_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee TANF"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50-.20",
        "Tennessee Administrative Code § 1240-01-50-.20 - Standard of Need/Income",
        "https://www.tn.gov/humanservices/for-families/families-first-tanf.html",
    )
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Check eligibility
        eligible = spm_unit("tn_tanf_eligible", period)

        # Get payment standard (SPA or DGPA based on eligibility)
        payment_standard = spm_unit("tn_tanf_payment_standard", period)

        # Calculate countable income
        countable_income = spm_unit("tn_tanf_countable_income", period)

        # Fill-the-gap budgeting: benefit = payment_standard - countable_income
        calculated_benefit = max_(payment_standard - countable_income, 0)

        # Apply minimum grant threshold
        p = parameters(period).gov.states.tn.dhs.tanf.benefit
        minimum_grant = p.minimum_grant

        # If benefit is less than minimum, no payment is made
        benefit = where(
            calculated_benefit >= minimum_grant, calculated_benefit, 0
        )

        # Only pay if eligible
        return where(eligible, benefit, 0)
