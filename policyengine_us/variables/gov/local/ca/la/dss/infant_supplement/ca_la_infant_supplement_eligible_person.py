from policyengine_us.model_api import *


class ca_la_infant_supplement_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible for the Los Angeles County infant supplement"
    defined_for = "in_la"

    def formula(person, period, parameters):
        foster_care = person("is_in_foster_care", period)
        is_parent = person("is_pregnant", period)
        age = person("age", period) * 12
        age_threshold = parameters(period).gov.local.ca.la.dss.age_threshold
        minor_dependent = age < age_threshold
        return foster_care & is_parent & minor_dependent
