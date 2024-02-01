from policyengine_us.model_api import *


class id_grocery_credit_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Idaho grocery credit"
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(person, period, parameters):
        # Incarcerated people are not eligible for the grocery credit
        return ~person("is_incarcerated", period)
