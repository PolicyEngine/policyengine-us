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
        # § 170(p) only allows cash contributions to § 170(b)(1)(A) organizations.
        # Known limitation: gifts to 509(a)(3) supporting orgs and donor-advised
        # funds cannot be separated with current inputs.
        cash_50 = add(tax_unit, period, ["resolved_charitable_cash_donations_50_pct"])
        filing_status = tax_unit("filing_status", period)
        return min_(p.non_itemizers_amount[filing_status], cash_50)
