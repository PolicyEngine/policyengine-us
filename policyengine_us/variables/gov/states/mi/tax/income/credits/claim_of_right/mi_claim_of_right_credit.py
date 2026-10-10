from policyengine_us.model_api import *


class mi_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan claim of right credit"
    unit = USD
    documentation = (
        "A filer who repays income taxed in an earlier year, and who is "
        "eligible for a deduction or credit under 26 U.S.C. 1341 for the "
        "repayment, may credit the Michigan tax paid in the earlier year on "
        "the repaid income (MCL 206.265(1)). The credit applies under either "
        "federal method, unless the repayment is deducted in calculating "
        "adjusted gross income, which claim_of_right_repayment excludes. Any "
        "excess over the year's tax is refunded (MCL 206.265(2)). Reported "
        "with Michigan tax withheld on Form MI-1040, line 31. Not modeled: "
        "before 2018, Revenue Administrative Bulletin 1994-9 also allowed "
        "the credit for a repayment of $3,000 or less that was deductible as "
        "a federal miscellaneous itemized deduction."
    )
    definition_period = YEAR
    reference = (
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-265",
        # Revenue Administrative Bulletin 1994-9
        "https://www.michigan.gov/treasury/reference/rab/content/1994/revenue-administrative-bulletin-1994-9",
        # 2025 MI-1040 instruction book, Repayments of Income Reported in a
        # Prior Year, and line 31
        "https://www.michigan.gov/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=8",
        "https://www.michigan.gov/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=12",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        # Section 1341 allows a deduction or credit when the repayment
        # exceeds the federal threshold.
        eligible = tax_unit("claim_of_right_section_1341_eligible", period)
        prior_year_tax = tax_unit("mi_claim_of_right_prior_year_tax_decrease", period)
        return where(eligible, prior_year_tax, 0)
