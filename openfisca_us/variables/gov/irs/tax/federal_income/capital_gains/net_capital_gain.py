from openfisca_us.model_api import *


class net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net capital gain"
    unit = USD
    documentation = "The excess of net long-term capital gain over net short-term capital loss."
    definition_period = YEAR

    formula = excess(of="net_long_term_capital_gain", over="net_short_term_capital_loss")
