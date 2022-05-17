from openfisca_us.model_api import *


class tax_unit_childcare_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Childcare expenses"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(["childcare_expenses"])
