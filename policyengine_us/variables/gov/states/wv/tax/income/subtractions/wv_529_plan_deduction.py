from policyengine_us.model_api import *


class wv_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia 529 plan contribution deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.smart529.com/learn/features-and-benefits.html",
        "https://code.wvlegislature.gov/11-21-12/",
    )
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        return tax_unit("investment_in_529_plan", period)
