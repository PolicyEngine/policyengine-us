from policyengine_us.model_api import *


class wi_income_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin subtractions from federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB.pdf"
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB-inst.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSBf.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSB-Inst.pdf"
    )
    defined_for = StateCode.WI
    adds = "gov.states.wi.tax.income.subtractions.sources"
