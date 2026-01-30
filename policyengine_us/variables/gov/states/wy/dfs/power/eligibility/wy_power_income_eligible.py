from policyengine_us.model_api import *


class wy_power_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wyoming POWER income eligible"
    definition_period = MONTH
    reference = (
        "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/table-ii-power-income-limits/",
        "https://dfs.wyo.gov/accordions/snap-and-power-policy-manual-1100-extended-menu/",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        # Income eligible if countable income < payment standard
        # (i.e., household would receive a positive benefit)
        # Note: The "Maximum Earned Income Limit" in Table II equals
        # payment_standard + earned_income_disregard, which is the
        # break-even point for earned-income-only households.
        countable_income = spm_unit("wy_power_countable_income", period)
        payment_standard = spm_unit("wy_power_payment_standard", period)
        return countable_income < payment_standard
