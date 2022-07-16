from openfisca_us.model_api import *


class md_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD income tax"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(
        ["md_income_tax_before_credits", "md_income_tax_credits"]
    )
