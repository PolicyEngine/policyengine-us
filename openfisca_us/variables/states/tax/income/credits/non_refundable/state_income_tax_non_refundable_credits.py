from openfisca_us.model_api import *


class state_income_tax_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "State non-refundable income tax credits"
    unit = USD
    documentation = "State non-refundable income tax credits"
    definition_period = YEAR

    formula = sum_of_variables(["state_limited_income_tax_credit"])
