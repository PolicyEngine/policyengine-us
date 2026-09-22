from policyengine_us.model_api import *


class or_kicker(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR Kicker"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=19",
        "https://www.oregonlegislature.gov/bills_laws/Pages/OrConst.aspx",  # Article IX Section 14 (4)
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["or"].tax.income.credits.kicker
        # The kicker is booked to the tax year whose liability determines it
        # (e.g. the 17.341% kicker is 17.341% of 2020 tax, so it is booked to
        # 2020), not the odd-numbered return year it is later claimed on. The
        # rate is therefore keyed to that determining year and applied to the
        # same year's tax before credits.
        return p.percent * tax_unit("or_income_tax_before_credits", period)
