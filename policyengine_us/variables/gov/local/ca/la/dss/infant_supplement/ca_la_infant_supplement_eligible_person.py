from policyengine_us.model_api import *


class ca_la_infant_supplement_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible for the Los Angeles County infant supplement"
    defined_for = "in_la"

    def formula(person, period, parameters):
        return person("ca_foster_care_minor_dependent", period)
