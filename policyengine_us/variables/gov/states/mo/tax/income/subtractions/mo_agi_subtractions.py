from policyengine_us.model_api import *


class mo_agi_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Missouri AGI subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mo.tax.income.subtractions
        total_subtractions = add(person, period, p.agi_subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
