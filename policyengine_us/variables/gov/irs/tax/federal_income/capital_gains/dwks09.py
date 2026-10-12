from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.capital_gains.schedule_d_tax_worksheet_form_4952_lines import (
    schedule_d_tax_worksheet_form_4952_lines,
)


class dwks09(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 2 of 6)"
    documentation = (
        "Schedule D Tax Worksheet line 9: the smaller of Schedule D line 15 "
        "or 16, less the part of any Form 4952 line 4g election attributed "
        "to net capital gain. Net capital gain other than qualified "
        "dividends, after 26 U.S.C. 1(h)(2)."
    )
    unit = USD
    reference = [
        dict(
            title="2025 Instructions for Schedule D, Schedule D Tax Worksheet, lines 3-9",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=15",
        ),
        dict(
            title="26 U.S. Code § 1(h)(2)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_2",
        ),
    ]

    def formula(tax_unit, period, parameters):
        lines = schedule_d_tax_worksheet_form_4952_lines(tax_unit, period)
        # Line 8: the smaller of line 3 or line 4, the part of the Form 4952
        # line 4g election that comes from net capital gain.
        line_8 = min_(lines.line_3, lines.line_4)
        # Line 9: line 7 minus line 8; if zero or less, zero.
        return max_(0, lines.line_7 - line_8)
