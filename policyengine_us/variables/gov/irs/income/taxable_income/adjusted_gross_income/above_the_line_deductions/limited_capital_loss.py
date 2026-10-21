from policyengine_us.model_api import *


class limited_capital_loss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Limited capital loss deduction"
    unit = USD
    documentation = (
        "The net capital loss deductible from gross income: the excess of "
        "capital losses over capital gains, including capital gain "
        "distributions, up to $3,000 ($1,500 if married filing separately). "
        "Schedule D line 21, as a positive number. Losses up to the gains "
        "are in capital_losses_allowed_against_gains."
    )
    definition_period = YEAR
    reference = (
        dict(
            title="26 U.S. Code § 1211(b) - Limitation on capital losses",
            href="https://www.law.cornell.edu/uscode/text/26/1211#b",
        ),
        dict(
            title="2025 Schedule D (Form 1040), lines 16 and 21",
            href="https://www.irs.gov/pub/irs-prior/f1040sd--2025.pdf#page=2",
        ),
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs
        filing_status = tax_unit("filing_status", period)
        max_loss = p.ald.loss.capital.max[filing_status]
        # As in capital_losses_allowed_against_gains: no capital loss
        # deduction when a reform takes capital gains out of gross income.
        if "capital_gains" not in p.gross_income.sources:
            return 0 * max_loss
        # A tax-unit dependent's capital losses belong on the dependent's own
        # return, as in irs_gross_income.
        capital_losses = tax_unit_non_dep_sum("capital_losses", tax_unit, period)
        # 26 U.S.C. 1211(b)(2): the excess of the losses over the gains.
        excess = capital_losses - tax_unit(
            "capital_losses_allowed_against_gains", period
        )
        return min_(max_loss, excess)
