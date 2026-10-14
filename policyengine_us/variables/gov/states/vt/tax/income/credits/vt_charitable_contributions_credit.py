from policyengine_us.model_api import *


class vt_charitable_contribution_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont charitable contribution credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/vermont/2022/title-32/chapter-151/section-5822/",
        "https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf#page=1",
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        cash_50 = add(tax_unit, period, ["charitable_cash_donations_50_pct_orgs"])
        cash_non_50 = add(
            tax_unit, period, ["charitable_cash_donations_non_50_pct_orgs"]
        )
        cash_total = add(tax_unit, period, ["charitable_cash_donations"])
        cash = where(cash_50 + cash_non_50 > 0, cash_50 + cash_non_50, cash_total)

        ord_50 = add(tax_unit, period, ["charitable_non_cash_donations_50_pct_orgs"])
        ord_non_50 = add(
            tax_unit, period, ["charitable_non_cash_donations_non_50_pct_orgs"]
        )
        ord_total = add(tax_unit, period, ["charitable_non_cash_donations"])
        non_cash = where(ord_50 + ord_non_50 > 0, ord_50 + ord_non_50, ord_total)

        cg = add(tax_unit, period, ["charitable_capital_gain_donations"])
        charitable_contributions = cash + non_cash + cg
        p = parameters(period).gov.states.vt.tax.income.credits
        return p.charitable.calc(charitable_contributions)
