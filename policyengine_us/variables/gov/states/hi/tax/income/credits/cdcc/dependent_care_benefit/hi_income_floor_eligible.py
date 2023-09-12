from policyengine_us.model_api import *


class hi_income_floor_eligible(Variable):
    value_type = float
    entity = Person
    label = "Hawaii income floor eligible"
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

        income = person("earned_income", period)

        return income