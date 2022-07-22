from openfisca_us.model_api import *


class taxable_pension_income(Variable):
    value_type = float
    entity = Person
    label = "Taxable pension income"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(["taxable_ira_income"])
