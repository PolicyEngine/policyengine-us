from openfisca_us.model_api import *


class tax_unit_interest_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit interest income"
    unit = USD
    documentation = "Tax unit interest income (excludes dependents)."
    definition_period = YEAR

    formula = sum_among_non_dependents("interest_income")
