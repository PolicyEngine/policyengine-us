from policyengine_us.model_api import *


class ks_liheap_countable_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Kansas LIEAP countable earned income"
    documentation = "Gross earned income counted toward Kansas LIEAP household income. Earned income of a child under 18 is not counted."
    unit = USD
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=6",
        "https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=7",
    )
    defined_for = StateCode.KS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ks.dcf.liheap.income
        earned = add(person, period, p.sources.earned)
        age = person("age", period)
        return where(age >= p.earned_income_min_age, earned, 0)
