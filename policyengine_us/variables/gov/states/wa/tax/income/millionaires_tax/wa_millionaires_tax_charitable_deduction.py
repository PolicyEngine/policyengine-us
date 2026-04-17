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
        charitable = add(
            tax_unit,
            period,
            ["charitable_cash_donations", "charitable_non_cash_donations"],
        )
        # Sec. 309: spouses filing separately split the combined cap.
        filing_status = tax_unit("filing_status", period)
        is_separate = filing_status == filing_status.possible_values.SEPARATE
        cap = where(
            is_separate,
            p.deductions.charitable.cap / 2,
            p.deductions.charitable.cap,
        )
        return min_(charitable, cap)
