from policyengine_us.model_api import *


class snap_excluded_child_earner(Variable):
    value_type = bool
    entity = Person
    label = "Excluded child earner"
    documentation = "Whether this person is a child whose earned income is excluded from SNAP "
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#d_7"

    def formula(person, period, parameters):
        p = p = parameters(period).gov.usda.snap.income
        age = person("monthly_age", period)
        is_in_k12_school = person("is_in_k12_school", period)
        age_eligible = age <= p.child_income_exclusion_age
        return is_in_k12_school & age_eligible
