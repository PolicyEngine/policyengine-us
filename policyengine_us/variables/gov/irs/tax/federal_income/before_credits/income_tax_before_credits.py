from policyengine_us.model_api import *


class income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "income tax before credits"
    unit = USD
    documentation = "Total (regular + AMT) income tax liability before credits"

    adds = [
        "income_tax_main_rates",
        "capital_gains_tax",
        "alternative_minimum_tax",
    ]
