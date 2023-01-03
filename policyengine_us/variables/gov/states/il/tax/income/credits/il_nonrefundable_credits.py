from openfisca_us.model_api import *


class il_nonrefundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL nonrefundable credits"
    unit = USD
    definition_period = YEAR
    reference = ""

    formula = sum_of_variables(
        "gov.states.il.tax.income.credits.list_of_nonrefundable_credits"
    )
