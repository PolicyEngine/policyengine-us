from policyengine_us.model_api import *


class charitable_deduction_for_non_itemizers(Variable):
    value_type = float
    entity = TaxUnit
    label = "Charitable deduction for non-itemizers"
    unit = USD
    documentation = (
        "Charitable deduction for non-itemizers under 26 U.S.C. 170(p), taken "
        "from adjusted gross income (2021 Form 1040 line 12b, and from 2026). "
        "The 2020 deduction for non-itemizers is above the line: "
        "charitable_contributions_ald."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/170#p",
        "https://www.irs.gov/newsroom/expanded-tax-benefits-help-individuals-and-businesses-give-to-charity-during-2021-deductions-up-to-600-available-for-cash-donations-by-non-itemizers",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.charity
        cash_donations = add(tax_unit, period, ["charitable_cash_donations"])
        filing_status = tax_unit("filing_status", period)
        return min_(p.non_itemizers_amount[filing_status], cash_donations)
