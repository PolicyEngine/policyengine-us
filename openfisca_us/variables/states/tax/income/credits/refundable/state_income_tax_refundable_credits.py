from openfisca_us.model_api import *


class state_income_tax_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax refundable credits"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(["state_eitc", "state_dependent_credit"])
