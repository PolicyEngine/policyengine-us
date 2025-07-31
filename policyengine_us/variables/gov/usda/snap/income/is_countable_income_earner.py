from policyengine_us.model_api import *


class is_countable_income_earner(Variable):
    value_type = bool
    entity = Person
    label = "Countable income earner"
    documentation = "Whether this person's earned income is counted for SNAP"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#d_7"

    def formula(person, period, parameters):
        p = p = parameters(period).gov.usda.snap.income
        age = person("monthly_age", period)
        is_in_k12_school = person("is_in_k12_school", period)
        age_eligible = age <= p.child_income_exclusion_age
        income_exclusion_child = is_in_k12_school & age_eligible
        return ~income_exclusion_child
