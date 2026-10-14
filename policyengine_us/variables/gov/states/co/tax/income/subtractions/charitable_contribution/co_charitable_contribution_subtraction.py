from policyengine_us.model_api import *


class co_charitable_contribution_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado charitable contribution subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=1+CCR+201-2&ruleVersionId=11214#page=15",
        # 1 CCR 201-2, Rule 39-22-104(4)(m)(1)
    )
    defined_for = "co_charitable_contribution_subtraction_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.co.tax.income.subtractions.charitable_contribution
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
        return max_(charitable_contributions - p.adjustment, 0)
