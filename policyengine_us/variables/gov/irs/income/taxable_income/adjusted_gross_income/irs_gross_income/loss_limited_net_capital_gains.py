from policyengine_us.model_api import *


class loss_limited_net_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Loss-limited net capital gains"
    documentation = (
        "The capital gain or loss on Form 1040 line 7a: Schedule D line 16 "
        "(long-term and short-term gains and losses, with capital gain "
        "distributions on line 13), or line 21 if line 16 is a loss. A filer "
        "with no other capital gains or losses reports the distributions "
        "without Schedule D, and the amount is the same."
    )
    unit = USD
    reference = (
        dict(
            title="26 U.S. Code § 1211(b) - Limitation on capital losses",
            href="https://www.law.cornell.edu/uscode/text/26/1211#b",
        ),
        dict(
            title="2025 Schedule D (Form 1040), lines 13, 16 and 21",
            href="https://www.irs.gov/pub/irs-prior/f1040sd--2025.pdf#page=2",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), Capital Gain Distributions",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=2",
        ),
        dict(
            title="2025 Instructions for Form 1040, line 7a, Exception 1",
            href="https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=31",
        ),
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs
        filing_status = tax_unit("filing_status", period)
        loss_limit = p.capital_gains.loss_limit[filing_status]
        net_capital_gains = tax_unit("net_capital_gains", period)
        # Capital gain distributions reported without Schedule D. A filer with
        # capital losses or other capital gains files Schedule D and enters
        # them on line 13, so they net against losses before the limit.
        distributions = add(tax_unit, period, ["non_sch_d_capital_gains"])
        return max_(-loss_limit, net_capital_gains + distributions)
