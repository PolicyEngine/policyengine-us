from openfisca_us.model_api import *


class tax_unit_earned_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit earned income"
    unit = USD
    definition_period = YEAR

    formula = sum_among_non_dependents("earned_income")
