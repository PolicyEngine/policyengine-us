from policyengine_us.model_api import *


class tce_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the TCE program"
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.tce.eligibility
        is_eligible_age = person("age", period) >= p.age_limit
        return is_eligible_age
