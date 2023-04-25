from policyengine_us.model_api import *
from microdf import MicroSeries


class household_income_decile(Variable):
    label = "household income decile"
    documentation = "Decile of household income (person-weighted)"
    entity = Household
    definition_period = YEAR
    value_type = int

    def formula(household, period, parameters):
        income = household("household_net_income", period)
        count_people = household("household_count_people", period)
        household_weight = household("household_weight", period)
        weighted_income = MicroSeries(
            income, weights=household_weight * count_people
        )
        return weighted_income.decile_rank().values
