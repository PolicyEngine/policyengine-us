from policyengine_us.model_api import *


class social_security_revenue(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Social Security revenue"
    documentation = "Total OASDI trust fund revenue from payroll taxes and benefit taxation"
    unit = USD

    def formula(tax_unit, period, parameters):
        payroll = add(
            tax_unit, period, ["payroll_tax_revenue_social_security"]
        )
        tob = tax_unit("tob_revenue_social_security", period)
        return payroll + tob
