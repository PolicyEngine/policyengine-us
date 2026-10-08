from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.capital_gains.schedule_d_tax_worksheet_form_4952_lines import (
    schedule_d_tax_worksheet_form_4952_lines,
)


class dividend_income_reduced_by_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Dividend income reduced by investment income"
    documentation = (
        "Schedule D Tax Worksheet line 6: qualified dividends less the part "
        "of any Form 4952 line 4g election not attributed to net capital "
        "gain. Qualified dividend income after 26 U.S.C. 1(h)(11)(D)(i)."
    )
    unit = USD
    reference = [
        dict(
            title="2025 Instructions for Schedule D, Schedule D Tax Worksheet, lines 2-6",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=15",
        ),
        dict(
            title="26 U.S. Code § 1(h)(11)(D)(i)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_11_D_i",
        ),
    ]

    def formula(tax_unit, period, parameters):
        # Line 2: qualified dividends (Form 1040 line 3a).
        line_2 = tax_unit("form_4952_qualified_dividends", period)
        lines = schedule_d_tax_worksheet_form_4952_lines(tax_unit, period)
        # Line 5: line 3 minus line 4; if zero or less, zero. The part of the
        # election that net capital gain from investment property cannot
        # cover comes from qualified dividends.
        line_5 = max_(0, lines.line_3 - lines.line_4)
        # Line 6: line 2 minus line 5; if zero or less, zero.
        return max_(0, line_2 - line_5)
