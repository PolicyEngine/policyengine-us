from policyengine_us.model_api import *


class wy_power_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wyoming POWER countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dfs.wyo.gov/accordions/snap-and-power-policy-manual-1100-extended-menu/",
        "https://wyoleg.gov/statutes/compress/title42.pdf#page=5",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        # Per Section 1101: Countable earned = Gross earned - Disregard
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        disregard = spm_unit("wy_power_earned_income_disregard", period)
        return max_(gross_earned - disregard, 0)
