from openfisca_us.model_api import *


class tax_unit_capital_loss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit capital loss"
    unit = USD
    documentation = "Total capital losses for the tax unit"
    definition_period = YEAR

    formula = sum_of_variables(["capital_loss"])
