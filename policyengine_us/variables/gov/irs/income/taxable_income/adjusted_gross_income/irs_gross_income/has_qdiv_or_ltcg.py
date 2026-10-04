from policyengine_us.model_api import *


class has_qdiv_or_ltcg(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Has qualified dividends or long-term capital gains"
    documentation = (
        "Whether this tax unit figures its tax with the Qualified Dividends "
        "and Capital Gain Tax Worksheet or the Schedule D Tax Worksheet: it "
        "has qualified dividends, or Schedule D lines 15 and 16 are both more "
        "than zero. Capital gain distributions are on Schedule D line 13, so "
        "a filer who reports them without Schedule D has lines 15 and 16 "
        "equal to them."
    )
    definition_period = YEAR
    reference = (
        dict(
            title="2025 Instructions for Form 1040, line 16",
            href="https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=36",
        ),
        dict(
            title="2025 Schedule D (Form 1040), lines 15 to 22",
            href="https://www.irs.gov/pub/irs-prior/f1040sd--2025.pdf#page=2",
        ),
    )

    def formula(tax_unit, period, parameters):
        qualified_dividends = add(tax_unit, period, ["qualified_dividend_income"])
        # Schedule D line 15: net long-term capital gain or loss, including
        # capital gain distributions (line 13).
        line_15 = add(
            tax_unit,
            period,
            ["long_term_capital_gains", "non_sch_d_capital_gains"],
        )
        # Schedule D line 16: line 15 plus the net short-term gain or loss.
        line_16 = line_15 + add(tax_unit, period, ["short_term_capital_gains"])
        return (qualified_dividends > 0) | ((line_15 > 0) & (line_16 > 0))
