from policyengine_us.model_api import *


class de_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Delaware subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.tax.income.subtractions
        total_subtractions = add(person, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
