from policyengine_us.model_api import *


class equiv_cbo_household_income(Variable):
    value_type = float
    entity = Household
    label = "Equivalized CBO household income"
    documentation = (
        "CBO household income adjusted for household size using the square "
        "root equivalence scale."
    )
    definition_period = YEAR
    unit = USD

    def formula(household, period, parameters):
        return (
            household("cbo_household_income", period)
            / household("household_size", period) ** 0.5
        )
