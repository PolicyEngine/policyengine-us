from policyengine_us.model_api import *


class short_term_capital_loss_carryover(Variable):
    value_type = float
    entity = Person
    label = "Short-term capital loss carryover"
    unit = USD
    documentation = (
        "Short-term capital loss carried to the year, as a positive amount: "
        "the person's own carryover under 26 U.S.C. 1212(b)(1)(A), on "
        "Schedule D line 6, plus any carryover allowed under 26 U.S.C. "
        "642(h)(1) from the final year of an estate or trust, on Schedule K-1 "
        "(Form 1041), box 11, code C, which is part of Schedule D line 5. The "
        "sum of own_short_term_capital_loss_carryover and "
        "estate_or_trust_short_term_capital_loss_carryover. A nonzero amount "
        "entered here for a year is filed as the person's own carryover when "
        "a Simulation or Microsimulation is built, in place of the leaves "
        "entered for that year. Memo item: short_term_capital_gains already "
        "includes it as a loss, as Schedule D line 7 does, so it does not "
        "change gross income or the net short-term capital loss on line 6 of "
        "the 28% Rate Gain Worksheet. The Arizona property tax credit adds it "
        "back."
    )
    definition_period = YEAR
    adds = [
        "own_short_term_capital_loss_carryover",
        "estate_or_trust_short_term_capital_loss_carryover",
    ]
    reference = [
        dict(
            title="26 U.S. Code § 1212(b)(1)(A)",
            href="https://www.law.cornell.edu/uscode/text/26/1212#b_1_A",
        ),
        dict(
            title="26 U.S. Code § 642(h)(1)",
            href="https://www.law.cornell.edu/uscode/text/26/642#h_1",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), Capital Loss Carryover Worksheet and 28% Rate Gain Worksheet #page 10-11",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=10",
        ),
        dict(
            title="2025 Instructions for Schedule K-1 (Form 1041) for a Beneficiary Filing Form 1040 or 1040-SR, Box 11, Codes C and D",
            href="https://www.irs.gov/pub/irs-prior/i1041sk1--2025.pdf#page=3",
        ),
    ]
