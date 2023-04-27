from policyengine_us.model_api import *


class ok_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        us_agi = tax_unit("adjusted_gross_income", period)
        ok_agi = tax_unit("ok_agi", period)
        prorate = min_(1, max_(0, where(us_agi != 0, ok_agi / us_agi, 0)))
        us_eitc = tax_unit("earned_income_tax_credit", period)
        p = parameters(period).gov.states.ok.tax.income.credits.earned_income
        return prorate * p.eitc_fraction * us_eitc
