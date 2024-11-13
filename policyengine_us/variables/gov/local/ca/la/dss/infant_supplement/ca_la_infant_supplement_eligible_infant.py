from policyengine_us.model_api import *


class ca_la_infant_supplement_eligible_infant(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Eligible Infant for the Los Angeles County infant supplement"
    defined_for = "in_la"

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.states.ca.infant
        return age <= p.age_limit
