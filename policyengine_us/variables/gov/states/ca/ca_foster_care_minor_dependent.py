from policyengine_us.model_api import *


class ca_foster_care_minor_dependent(Variable):
    value_type = bool
    entity = Person
    label = "California foster care minor dependent"
    definition_period = MONTH
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        age = person("monthly_age", period)
        p = parameters(period).gov.states.ca.foster_care
        age_eligible = age < p.age_threshold
        in_foster_care = person("is_in_foster_care", period)
        return age_eligible & in_foster_care
