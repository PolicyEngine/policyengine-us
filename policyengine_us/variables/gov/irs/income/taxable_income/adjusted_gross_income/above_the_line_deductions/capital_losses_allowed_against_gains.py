from policyengine_us.model_api import *


class capital_losses_allowed_against_gains(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capital losses allowed against capital gains"
    unit = USD
    documentation = (
        "Capital losses deducted to the extent of capital gains, the first "
        "part of the allowance in 26 U.S.C. 1211(b). Gross income includes "
        "each filer's net capital gain and capital gain distributions, but "
        "not losses; this deduction nets the losses against those gains, as "
        "Schedule D does with capital gain distributions on line 13. "
        "limited_capital_loss is the second part, the net loss up to the "
        "$3,000 limit."
    )
    definition_period = YEAR
    reference = (
        dict(
            title="26 U.S. Code § 1211(b) - Limitation on capital losses",
            href="https://www.law.cornell.edu/uscode/text/26/1211#b",
        ),
        dict(
            title="26 U.S. Code § 62(a)(3) - Losses from sale or exchange of property",
            href="https://www.law.cornell.edu/uscode/text/26/62#a_3",
        ),
        dict(
            title="26 U.S. Code § 852(b)(3)(B) - Capital gain dividends",
            href="https://www.law.cornell.edu/uscode/text/26/852#b_3_B",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), Capital Gain Distributions",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=2",
        ),
    )

    def formula(tax_unit, period, parameters):
        sources = parameters(period).gov.irs.gross_income.sources
        person = tax_unit.members
        # A tax-unit dependent's capital gains and losses belong on the
        # dependent's own return, as in irs_gross_income.
        not_dependent = ~person("is_tax_unit_dependent", period)
        # The capital gains irs_gross_income counts: each filer's net gain
        # from sales and exchanges, and capital gain distributions reported
        # without Schedule D. Capital gain distributions are long-term capital
        # gains (26 U.S.C. 852(b)(3)(B)), and a filer with capital losses
        # enters them on Schedule D line 13, where they net against the
        # losses.
        gains = 0
        for source in ["capital_gains", "non_sch_d_capital_gains"]:
            if source in sources:
                gains += max_(0, person(source, period))
        gains_in_gross_income = tax_unit.sum(not_dependent * gains)
        capital_losses = tax_unit_non_dep_sum("capital_losses", tax_unit, period)
        return min_(capital_losses, gains_in_gross_income)
