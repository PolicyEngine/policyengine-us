from openfisca_us.model_api import *


class c05800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax before credits"
    unit = USD
    documentation = "Total (regular + AMT) income tax liability before credits"

    formula = sum_of_variables(
        [
            "income_tax_main_rates",
            "capital_gains_tax",
            "alternative_minimum_tax",
        ]
    )


income_tax_before_credits = variable_alias("income_tax_before_credits", c05800)
