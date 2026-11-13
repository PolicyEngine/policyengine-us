from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.federal_income.capital_gains.filer_schedule_d_lines import (
    filer_schedule_d_lines,
)


class has_qdiv_or_ltcg(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Has qualified dividends or long-term capital gains"
    documentation = (
        "Whether this tax unit figures its tax with the Qualified Dividends "
        "and Capital Gain Tax Worksheet or the Schedule D Tax Worksheet: the "
        "head and spouse have qualified dividends, or their Schedule D lines "
        "15 and 16 are both more than zero. Capital gain distributions are on "
        "Schedule D line 13, so a filer who reports them without Schedule D "
        "has lines 15 and 16 equal to them."
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
        # Form 1040 line 3a and Schedule D lines 15 and 16 of the head and
        # spouse; a tax unit dependent's dividends, gains and losses are on
        # the dependent's own return.
        qualified_dividends = tax_unit_non_dep_add(
            tax_unit, period, ["qualified_dividend_income"]
        )
        lines = filer_schedule_d_lines(tax_unit, period)
        return (qualified_dividends > 0) | ((lines.line_15 > 0) & (lines.line_16 > 0))
