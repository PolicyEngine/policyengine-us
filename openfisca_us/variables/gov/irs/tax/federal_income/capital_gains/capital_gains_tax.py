from openfisca_us.model_api import *


class capital_gains_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum income tax after capital gains tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        net_cg = tax_unit("net_capital_gain", period)
        adjusted_net_cg = tax_unit("adjusted_net_capital_gain", period)

        cg_rates = parameters(period).irs.capital_gains.brackets
        taxable_income = tax_unit("taxable_income", period)

        income_less_ncg = taxable_income - net_cg
        income_less_ancg = taxable_income - adjusted_net_cg
