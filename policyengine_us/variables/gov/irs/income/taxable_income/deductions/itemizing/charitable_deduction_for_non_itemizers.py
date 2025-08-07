from policyengine_us.model_api import *


class charitable_deduction_for_non_itemizers(Variable):
    value_type = float
    entity = TaxUnit
    label = "Charitable deduction for non-itemizers"
    unit = USD
    documentation = "Charitable deduction amount for non-itemizers."
    definition_period = YEAR
    reference = "https://www.irs.gov/newsroom/expanded-tax-benefits-help-individuals-and-businesses-give-to-charity-during-2021-deductions-up-to-600-available-for-cash-donations-by-non-itemizers"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.charity
        cash_donations = add(tax_unit, period, ["charitable_cash_donations"])
        filing_status = tax_unit("filing_status", period)
        return min_(p.non_itemizers_amount[filing_status], cash_donations)
