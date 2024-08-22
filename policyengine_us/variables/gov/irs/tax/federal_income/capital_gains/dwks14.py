from policyengine_us.model_api import *


class dwks14(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 5 of 6)"
    unit = USD

    def formula(tax_unit, period, parameters):
        dwks01 = tax_unit("taxable_income", period)
        dwks13 = tax_unit("dwks13", period)
        return max_(0, dwks01 - dwks13) * tax_unit("has_qdiv_or_ltcg", period)
