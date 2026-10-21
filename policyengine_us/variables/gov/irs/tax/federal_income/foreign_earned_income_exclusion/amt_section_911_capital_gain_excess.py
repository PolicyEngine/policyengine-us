from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.foreign_earned_income_exclusion.schedule_d_tax_worksheet_after_capital_gain_excess import (
    schedule_d_tax_worksheet_after_capital_gain_excess,
)


class amt_section_911_capital_gain_excess(Variable):
    value_type = float
    entity = TaxUnit
    label = "AMT section 911 capital gain excess"
    unit = USD
    documentation = (
        "For a taxpayer excluding foreign earned income under 26 U.S.C. "
        "911(a), the excess of line 10 of the Schedule D Tax Worksheet over "
        "the AMT taxable excess (Form 6251 line 6). The capital gains used in "
        "Form 6251 Part III are reduced by this excess. Reported for "
        "reference: amt_tax_including_cg figures it itself, so an input here "
        "does not change the AMT."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 911(f)(2)(B)(i)",
            href="https://www.law.cornell.edu/uscode/text/26/911#f_2_B_i",
        ),
        dict(
            title="2025 Form 6251 instructions, Part III, Form 2555",
            href="https://www.irs.gov/pub/irs-pdf/i6251.pdf#page=13",
        ),
    ]

    def formula(tax_unit, period, parameters):
        # Form 6251 instructions: "subtract Form 6251, line 6, from line 4 of
        # your AMT Qualified Dividends and Capital Gain Tax Worksheet or line
        # 10 of your AMT Schedule D Tax Worksheet". amt_tax_including_cg
        # applies it through schedule_d_tax_worksheet_after_capital_gain_excess.
        return schedule_d_tax_worksheet_after_capital_gain_excess(
            tax_unit, period, tax_unit("amt_income_less_exemptions", period)
        ).capital_gain_excess
