from policyengine_us.model_api import *


class ss_retirement_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Eligible for Social Security retirement benefits"
    documentation = (
        "Whether a person's claiming age meets the minimum "
        "retirement age for Social Security retirement benefits"
    )
    reference = "https://www.ssa.gov/benefits/retirement/planner/agereduction.html"

    def formula(person, period, parameters):
        claiming_age = person("ss_claiming_age", period)
        p = parameters(period).gov.ssa.social_security
        return claiming_age >= p.minimum_retirement_age
