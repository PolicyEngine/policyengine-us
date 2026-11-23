from policyengine_us.model_api import *


class census_household_money_income(Variable):
    value_type = float
    entity = Household
    label = "Census household money income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Census Bureau money income of the household: census_money_income "
        "summed over every member. Census sums the money income of household "
        "members 15 and older; this total also counts any amount the model "
        "gives a younger member."
    )
    reference = (
        "https://www2.census.gov/programs-surveys/cps/methodology/Appendix%20A%20P60-200%20income%20measurement%20definition.pdf#page=1",
        "https://cps.ipums.org/cps-action/variables/HHINCOME",
    )
    adds = ["census_money_income"]
