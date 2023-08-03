from openfisca_us.model_api import *


class in_taxes_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN taxes before credits"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(
        [
            "in_agi_tax",
            "in_county_tax",
            "in_other_taxes",
        ]
    )
