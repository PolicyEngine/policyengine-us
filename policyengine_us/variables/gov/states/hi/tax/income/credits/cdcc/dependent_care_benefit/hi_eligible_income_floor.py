from policyengine_us.model_api import *


class hi_eligible_income_floor(Variable):
    value_type = float
    entity = Person
    label = "Hawaii eligible income floor"
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
        p = parameters(period).gov.states.hi.tax.income.credits.cdcc
        qualified_children = person.tax_unit("count_cdcc_eligible", period)
        # Floor depends on number of eligible dependents
        income_floor = p.disabled_student_income_floor.calc(qualified_children)
        income = person("earned_income", period)

        return max_(income, income_floor)
