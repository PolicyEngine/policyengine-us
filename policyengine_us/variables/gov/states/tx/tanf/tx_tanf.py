from policyengine_us.model_api import *


class tx_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits",
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/c-110-tanf",
    )
    defined_for = "tx_tanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("tx_tanf_payment_standard", period)
        countable_income = spm_unit("tx_tanf_countable_income", period)
        p = parameters(period).gov.states.tx.tanf

        # Calculate benefit as payment standard minus countable income
        calculated_benefit = max_(payment_standard - countable_income, 0)

        # Apply minimum grant rule
        minimum_grant = p.minimum_grant

        # Debug: Check if the calculated benefit is being computed correctly
        # This will help us understand what's happening

        # If calculated benefit is positive but less than minimum, use minimum
        # If calculated benefit is zero, remain zero
        benefit_amount = where(
            (calculated_benefit > 0) & (calculated_benefit < minimum_grant),
            minimum_grant,
            calculated_benefit,
        )

        return benefit_amount
