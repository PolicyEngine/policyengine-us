from openfisca_us.model_api import *


class taxsim_ltcg(Variable):
    value_type = float
    entity = TaxUnit
    label = "Long-term capital gains"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["long_term_capital_gains"])
