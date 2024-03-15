from policyengine_us.model_api import *


class hi_alternative_tax_on_capital_gains_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Hawaii alternative tax on capital gains"
    definition_period = YEAR
    defined_for = StateCode.HI

    # The tax form spcifies an income threshold which is not defined in the law
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.alternative_tax
        net_capital_gains = tax_unit("net_capital_gain", period)
        return p.availability & (net_capital_gains > 0)
