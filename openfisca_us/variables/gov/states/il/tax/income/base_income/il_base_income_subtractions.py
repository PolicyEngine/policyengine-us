from openfisca_us.model_api import *


class il_base_income_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL base income subtractions"
    unit = USD
    definition_period = YEAR
    reference = ""

    formula = sum_of_variables("gov.states.il.tax.income.base.subtractions")
