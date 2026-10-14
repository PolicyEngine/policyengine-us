from policyengine_us.model_api import *


class wa_millionaires_tax_charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington millionaires tax charitable deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=13"
    defined_for = "wa_millionaires_tax_applies"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wa.tax.income.millionaires_tax
        cash_50 = add(tax_unit, period, ["charitable_cash_donations_50_pct_orgs"])
        cash_non_50 = add(
            tax_unit, period, ["charitable_cash_donations_non_50_pct_orgs"]
        )
        cash_total = add(tax_unit, period, ["charitable_cash_donations"])
        cash = where(cash_50 + cash_non_50 > 0, cash_50 + cash_non_50, cash_total)

        ord_50 = add(tax_unit, period, ["charitable_non_cash_donations_50_pct_orgs"])
        ord_non_50 = add(
            tax_unit,
            period,
            ["charitable_non_cash_donations_non_50_pct_orgs"],
        )
        ord_total = add(tax_unit, period, ["charitable_non_cash_donations"])
        non_cash = where(ord_50 + ord_non_50 > 0, ord_50 + ord_non_50, ord_total)

        cg = add(tax_unit, period, ["charitable_capital_gain_donations"])
        charitable = cash + non_cash + cg
        # Sec. 309: spouses filing separately split the combined cap.
        filing_status = tax_unit("filing_status", period)
        is_separate = filing_status == filing_status.possible_values.SEPARATE
        cap = where(
            is_separate,
            p.deductions.charitable.cap / 2,
            p.deductions.charitable.cap,
        )
        return min_(charitable, cap)
