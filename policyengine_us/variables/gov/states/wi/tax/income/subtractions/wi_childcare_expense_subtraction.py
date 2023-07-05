from policyengine_us.model_api import *


class wi_childcare_expense_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "WI childcare expense subtraction from federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB.pdf"
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB-inst.pdf#page=7"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        return 0
