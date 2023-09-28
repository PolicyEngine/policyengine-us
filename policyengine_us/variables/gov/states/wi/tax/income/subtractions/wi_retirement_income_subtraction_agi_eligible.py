from policyengine_us.model_api import *


class wi_retirement_income_subtraction_agi_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Wisconsin retirement income subtraction AGI eligibility"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB.pdf"
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB-inst.pdf#page=9"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSBf.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSB-Inst.pdf#page=7"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        fstatus = tax_unit("filing_status", period)
        p = parameters(period).gov.states.wi.tax.income
        return agi < p.subtractions.retirement_income.max_agi[fstatus]
