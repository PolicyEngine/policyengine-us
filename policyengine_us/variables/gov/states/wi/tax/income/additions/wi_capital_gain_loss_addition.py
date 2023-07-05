from policyengine_us.model_api import *


class wi_capital_gain_loss_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "WI capital gain/loss addition to federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleAD.pdf"
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleAD-inst.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleADf.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleAD-Inst.pdf#page=2"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        return 0
