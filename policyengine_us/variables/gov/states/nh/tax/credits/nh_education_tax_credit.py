from policyengine_us.model_api import *


class nh_education_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire Education Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://gc.nh.gov/rsa/html/NHTOC/NHTOC-V-77-G.htm"
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nh.tax.credits.education

        # Get Rate for donation
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
        donation = cash + non_cash + cg
        return p.rate.calc(donation)
