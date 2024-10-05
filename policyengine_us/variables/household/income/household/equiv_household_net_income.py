from policyengine_us.model_api import *


class equiv_household_net_income(Variable):
    value_type = float
    entity = Household
    label = "equivalised net income"
    definition_period = YEAR
    unit = USD

    def formula(household, period, parameters):
        number_of_people = household("household_size", period)
        net_income = household("household_net_income", period)
        return net_income / (number_of_people**0.5)
