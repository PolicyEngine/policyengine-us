from policyengine_us.model_api import *


class ss_retirement_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Eligible for Social Security retirement benefits"
    documentation = "Whether a person is at least 62 years old and eligible for Social Security retirement benefits"
    reference = (
        "https://www.ssa.gov/benefits/retirement/planner/agereduction.html"
    )

    def formula(person, period, parameters):
        age = person("age", period)
        # Must be at least 62 to receive retirement benefits
        return age >= 62
