from policyengine_us.model_api import *


class wy_power_earned_income_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wyoming POWER earned income disregard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://wyoleg.gov/statutes/compress/title42.pdf#page=5",
        "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/",
    )
    defined_for = StateCode.WY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wy.dfs.power.income.disregard
        # Per W.S. 42-2-103: $1,200 for married couple with child in common,
        # $600 for single parent or each working applicant in two-parent unit
        is_married = spm_unit("spm_unit_is_married", period.this_year)
        person = spm_unit.members
        has_child = spm_unit.any(person("age", period.this_year) < 18)
        married_with_child = is_married & has_child

        return where(
            married_with_child,
            p.married_couple,
            p.individual,
        )
