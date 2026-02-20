from policyengine_us.model_api import *


class tx_regular_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "Texas Temporary Assistance for Needy Families (TANF) regular benefit"
    )
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
        capped_benefit = min_(calculated_benefit, payment_standard)

        # Apply minimum grant rule
        return max_(capped_benefit, p.minimum_grant)
