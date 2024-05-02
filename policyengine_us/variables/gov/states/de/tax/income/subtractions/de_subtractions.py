from policyengine_us.model_api import *


class de_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Delaware subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    adds = "gov.states.de.tax.income.subtractions.subtractions"
