from policyengine_us.model_api import *


class long_term_capital_loss_carryover(Variable):
    value_type = float
    entity = Person
    label = "Long-term capital loss carryover"
    unit = USD
    documentation = (
        "Long-term capital loss carried to the year under 26 U.S.C. "
        "1212(b)(1)(B), as a positive amount: the person's own carryover on "
        "Schedule D line 14 plus any carryover on Schedule K-1 (Form 1041), "
        "box 11, code D, from the final year of an estate or trust, which is "
        "part of Schedule D line 12 (together, line 5 of the 28% Rate Gain "
        "Worksheet and line 16 of the Unrecaptured Section 1250 Gain "
        "Worksheet). The sum of own_long_term_capital_loss_carryover and "
        "estate_or_trust_long_term_capital_loss_carryover; an amount entered "
        "here for a year is used for that year instead, for every person in "
        "the simulation (zero for anyone it is not entered for), so enter "
        "either the sum or the leaves. Memo item: "
        "long_term_capital_gains already includes it as a loss, as Schedule D "
        "line 15 does, so it does not change gross income. It reduces "
        "collectibles_gain_or_loss and section_1202_gain in the 28-percent "
        "rate gain, and what they do not absorb reduces "
        "unrecaptured_section_1250_gain_before_losses."
    )
    definition_period = YEAR
    adds = [
        "own_long_term_capital_loss_carryover",
        "estate_or_trust_long_term_capital_loss_carryover",
    ]
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(4)(B)(iii)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_4_B_iii",
        ),
        dict(
            title="26 U.S. Code § 1212(b)(1)(B)",
            href="https://www.law.cornell.edu/uscode/text/26/1212#b_1_B",
        ),
        dict(
            title="26 U.S. Code § 642(h)(1)",
            href="https://www.law.cornell.edu/uscode/text/26/642#h_1",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), 28% Rate Gain Worksheet—Line 18, line 5",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=11",
        ),
    ]
