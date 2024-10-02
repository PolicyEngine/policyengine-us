from policyengine_us.model_api import *


class in_agi_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana adjusted gross income tax"
    definition_period = YEAR
    unit = USD
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-1"  # (a)(3)
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income
        in_agi = tax_unit("in_agi", period)
        return max_(0, in_agi * p.agi_rate)
