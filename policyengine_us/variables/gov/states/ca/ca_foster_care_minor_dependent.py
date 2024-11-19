from policyengine_us.model_api import *


class ca_foster_care_minor_dependent(Variable):
    value_type = bool
    entity = Person
    label = "California foster care minor dependent"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        age = person("age", period) * MONTHS_IN_YEAR
        age_threshold = parameters(period).gov.local.ca.la.dss.age_threshold
        age_eligible = age < age_threshold
        in_foster_care = person("is_in_foster_care", period)
        return age_eligible & in_foster_care
