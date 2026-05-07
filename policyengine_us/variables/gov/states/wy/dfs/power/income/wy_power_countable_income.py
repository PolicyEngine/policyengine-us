from policyengine_us.model_api import *


class wy_power_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wyoming POWER countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dfs.wyo.gov/accordions/snap-and-power-policy-manual-1100-extended-menu/",
        "https://wyoleg.gov/statutes/compress/title42.pdf#page=5",
    )
    defined_for = StateCode.WY
    # Per Section 1101: Countable income = Countable earned + Gross unearned
    adds = [
        "wy_power_countable_earned_income",
        "tanf_gross_unearned_income",
    ]
