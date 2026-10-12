from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.foreign_earned_income_exclusion.schedule_d_tax_worksheet_after_capital_gain_excess import (
    schedule_d_tax_worksheet_after_capital_gain_excess,
)


class dwks19(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 6 of 6)"
    documentation = (
        "Schedule D Tax Worksheet line 21 (line 19 of the 2017 and 2018 "
        "worksheets): the part of taxable income taxed at the regular rates, "
        "26 U.S.C. 1(h)(1)(A). Form 6251 Part III line 27 uses it."
    )
    unit = USD
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(1)(A)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_1_A",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), Schedule D Tax Worksheet, lines 18 to 21",
            href="https://www.irs.gov/pub/irs-pdf/i1040sd.pdf#page=15",
        ),
    ]

    def formula(tax_unit, period, parameters):
        dwks14 = tax_unit("dwks14", period)
        # Line 1 is taxable income, or for a Form 2555 filer line 3 of the
        # Foreign Earned Income Tax Worksheet, and line 10 reflects any
        # capital gain excess.
        dwks01 = tax_unit("taxable_income_plus_section_911_exclusion", period)
        dwks10 = schedule_d_tax_worksheet_after_capital_gain_excess(
            tax_unit, period, tax_unit("taxable_income", period)
        ).line_10
        # Line 18: line 1 less line 10 (section 1(h)(1)(A)(i)).
        line_18 = max_(0, dwks01 - dwks10)
        # Line 19: the smaller of line 1 or the top of the 24 percent
        # bracket, the taxable income taxed at a rate below 25 percent
        # (section 1(h)(1)(A)(ii)(I)).
        line_19 = tax_unit("taxable_income_taxed_below_25_percent", period)
        # Line 20: the smaller of line 14 or line 19 (section 1(h)(1)(A)(ii)).
        line_20 = min_(dwks14, line_19)
        # Line 21: the larger of line 18 or line 20. Without 28 percent rate
        # or unrecaptured section 1250 gain, line 13 is line 10, so lines 18
        # and 21 are line 14.
        return max_(line_18, line_20) * tax_unit("has_qdiv_or_ltcg", period)
