from policyengine_us.model_api import *


class ca_la_expectant_parent_payment_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Eligible for the Los Angeles County expectant parent paymentt"
    defined_for = "in_la"

    def formula(person, period, parameters):
        foster_care = person("is_in_foster_care", period)
        is_pregnant = person("is_pregnant", period)
        return foster_care & is_pregnant
