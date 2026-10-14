from policyengine_us.model_api import *


class nyc_income_tax_elimination_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC income tax elimination credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/1310",
        "https://www.tax.ny.gov/pdf/2025/inc/it270_2025_fill_in.pdf#page=1",
        "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=21",
    )
    defined_for = "nyc_income_tax_elimination_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.local.ny.nyc.tax.income.credits.income_tax_elimination
        # Form IT-270 lines 1 to 5 (Tax Law § 1310(h)(2)): the credit falls in
        # proportion to federal adjusted gross income above the threshold and
        # reaches zero at the phase-out width. Line 5 rounds the fraction to
        # the fourth decimal place.
        agi = tax_unit("adjusted_gross_income", period)
        threshold = tax_unit(
            "nyc_income_tax_elimination_credit_income_threshold", period
        )
        excess = max_(agi - threshold, 0)
        width = p.phase_out_width
        fraction = round_(max_(width - excess, 0) / width, 4)
        # Lines 6 to 10 (§ 1310(h)(1)): Form IT-201 line 54, the NYC tax after
        # the household credit and NYC nonrefundable credits, less the other
        # Article 30 credits claimed as refundable credits. The NYC school tax
        # credit is a State credit under Tax Law § 606(ggg), not an Article 30
        # credit, so it does not reduce this amount.
        tax = tax_unit("nyc_income_tax_before_refundable_credits", period)
        other_credits = add(tax_unit, period, ["nyc_cdcc", "nyc_eitc"])
        return max_(tax - other_credits, 0) * fraction
