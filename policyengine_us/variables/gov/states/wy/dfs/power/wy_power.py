from policyengine_us.model_api import *


class wy_power(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wyoming POWER benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/",
        "https://dfs.wyo.gov/accordions/snap-and-power-policy-manual-1100-extended-menu/",
    )
    defined_for = "wy_power_eligible"

    def formula(spm_unit, period, parameters):
        # Per Section 1101: Benefit = Payment Standard - Countable Income
        payment_standard = spm_unit("wy_power_payment_standard", period)
        countable_income = spm_unit("wy_power_countable_income", period)
        benefit = max_(payment_standard - countable_income, 0)
        return min_(benefit, payment_standard)
