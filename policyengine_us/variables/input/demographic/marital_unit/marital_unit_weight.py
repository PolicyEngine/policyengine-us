from policyengine_us.model_api import *


class marital_unit_weight(Variable):
    value_type = float
    entity = MaritalUnit
    label = "Marital unit weight"
    definition_period = YEAR

    def formula(marital_unit, period, parameters):
        # If no weight provided, use the average of the people in the marital unit.
        return marital_unit.household("household_weight", period)
