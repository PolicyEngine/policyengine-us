from policyengine_us.model_api import *


class household_size(Variable):
    value_type = int
    entity = Household
    label = "Household size"
    definition_period = YEAR

    def formula(household, period, parameters):
        return household.nb_persons()
