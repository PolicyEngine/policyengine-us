from policyengine_us.model_api import *


class ss_aime_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Eligible for AIME calculation"
    documentation = (
        "Whether person is old enough for AIME calculation to apply"
    )

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.ssa.social_security.aime
        return age >= p.minimum_age_for_earnings
