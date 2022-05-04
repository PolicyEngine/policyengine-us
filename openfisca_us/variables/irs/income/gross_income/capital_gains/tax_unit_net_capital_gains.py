from openfisca_us.model_api import *


class tax_unit_net_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit net capital gains"
    unit = USD
    documentation = "Tax unit net capital gains."
    definition_period = YEAR
