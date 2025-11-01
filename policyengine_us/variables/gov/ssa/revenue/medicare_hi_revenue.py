from policyengine_us.model_api import *


class medicare_hi_revenue(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Medicare HI revenue"
    documentation = "Total Medicare HI trust fund revenue from payroll taxes and benefit taxation"
    unit = USD

    def formula(tax_unit, period, parameters):
        payroll = add(tax_unit, period, ["payroll_tax_revenue_medicare"])
        tob = tax_unit("tob_revenue_medicare_hi", period)
        return payroll + tob
