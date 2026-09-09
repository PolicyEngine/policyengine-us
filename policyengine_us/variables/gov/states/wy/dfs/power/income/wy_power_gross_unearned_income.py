from policyengine_us.model_api import *


class wy_power_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Wyoming POWER gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/"
    defined_for = StateCode.WY

    adds = "gov.states.wy.dfs.power.income.sources.unearned"
