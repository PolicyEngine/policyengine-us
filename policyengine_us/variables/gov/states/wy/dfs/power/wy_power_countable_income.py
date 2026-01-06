from policyengine_us.model_api import *


class wy_power_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wyoming POWER countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dfs.wyo.gov/accordions/snap-and-power-policy-manual-1100-extended-menu/",
        "https://codes.findlaw.com/wy/title-42-welfare/wy-st-sect-42-2-103.html",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        # Per Section 1101: Countable income = (Earned - Disregard) + Unearned
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        disregard = spm_unit("wy_power_earned_income_disregard", period)
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])

        # Apply disregard to earned only, then add unearned
        return max_(gross_earned - disregard, 0) + gross_unearned
