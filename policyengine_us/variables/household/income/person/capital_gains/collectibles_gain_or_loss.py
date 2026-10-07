from policyengine_us.model_api import *


class collectibles_gain_or_loss(Variable):
    value_type = float
    entity = Person
    label = "Collectibles gain or loss before netting"
    unit = USD
    documentation = (
        "Gain, or deductible loss, from the sale or exchange of collectibles "
        "held as capital assets for more than one year, negative for a net "
        "loss, before the losses the 28% Rate Gain Worksheet nets against "
        "it: lines 1, 3 and 4 of that worksheet. capital_gains_28_percent_rate_gain "
        "nets it with section 1202 gain, the net short-term capital loss and "
        "the long-term capital loss carryover. Memo item: "
        "long_term_capital_gains already includes it. For an amount already "
        "netted, as on Schedule D line 18, use "
        "long_term_capital_gains_on_collectibles; enter one or the other. "
        "Federal only: Massachusetts' collectibles deduction reads "
        "long_term_capital_gains_on_collectibles."
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.long_term_capital_gains"
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(4)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_4",
        ),
        dict(
            title="26 U.S. Code § 1(h)(5)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_5",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), 28% Rate Gain Worksheet—Line 18, lines 1, 3 and 4",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=11",
        ),
    ]
