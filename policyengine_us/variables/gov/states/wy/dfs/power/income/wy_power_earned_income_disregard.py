from policyengine_us.model_api import *


class wy_power_earned_income_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wyoming POWER earned income disregard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://wyoleg.gov/statutes/compress/title42.pdf#page=10",
        "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wy.dfs.power.income.disregard
        # Per W.S. 42-2-103(a)(iv): $600 for any one recipient,
        # $1,200 for married couples
        is_married = add(spm_unit, period, ["is_tax_unit_head_or_spouse"]) > 1
        return where(is_married, p.married_couple, p.individual)
