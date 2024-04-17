from policyengine_us.model_api import *


class wi_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin additions to federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleAD.pdf"
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleAD-inst.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleADf.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleAD-Inst.pdf"
    )
    defined_for = StateCode.WI
    adds = "gov.states.wi.tax.income.additions.sources"
