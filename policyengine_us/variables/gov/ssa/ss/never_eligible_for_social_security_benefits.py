from policyengine_us.model_api import *


class never_eligible_for_social_security_benefits(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Never eligible for Social Security"
    unit = USD

    def formula(person, period, parameters):
        # Assumption: if person is above age 70 and has no social security benefits, then they are never eligible.
        age = person("age", period)
        social_security = person("social_security", period)
        return (age >= 70) & (social_security == 0)
