from policyengine_us.model_api import *


class in_agi_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN adjusted gross income tax"
    definition_period = YEAR
    unit = USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-1"  # (a)(3)

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.taxes.agi
        in_agi = tax_unit("in_agi", period)
        return in_agi * p.rate
