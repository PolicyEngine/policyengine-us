from policyengine_us.model_api import *


class alternative_tax_on_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii alternative tax on capital gains"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("taxable_income", period)
        # federal_lt_capital_gain = max_(0,add(person, period, ["long_term_capital_gains"])) # neagative? 
        # federal_st_capital_gain = max_(0,add(person, period, ["long_term_capital_gains"])) # negative?

        federal_net_capital_gain = tax_unit("net_capital_gain", period)
        # Hawaii_net_capital_gain = lt_adjustments + federal_net capital gain + st_adjustments

        federal_lt_capital_gain = add(person, period, ["long_term_capital_gains"])
        # Hawaii_net_lt_capital_gain = federal_lt_capital_gain + lt_adjustments
        # 
        return 1