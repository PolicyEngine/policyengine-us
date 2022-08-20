from openfisca_us.model_api import *


class school_meal_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Countable income for school meals"
    documentation = "SPM unit's countable income for school meal program"

    formula = sum_of_variables("gov.usda.school_meals.income.sources")
