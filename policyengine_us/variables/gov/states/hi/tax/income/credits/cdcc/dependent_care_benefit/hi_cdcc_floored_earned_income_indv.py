from policyengine_us.model_api import *


class hi_cdcc_floored_earned_income_indv(Variable):
    value_type = float
    entity = Person
    label = "Hawaii minimum income between head and spouse for the CDCC"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=28"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=29"
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=41"
        "https://files.hawaii.gov/tax/forms/2022/schx_i.pdf#page=2"
    )

    def formula(person, period, parameters):
        floor = person("hi_cdcc_eligible_income_floor", period)
        earnings = person("earned_income", period)
        return max_(floor, earnings)
