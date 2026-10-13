from policyengine_us.model_api import *


class short_term_capital_loss_carryover(Variable):
    value_type = float
    entity = Person
    label = "Short-term capital loss carryover"
    unit = USD
    documentation = (
        "Short-term capital loss carried to the year under 26 U.S.C. "
        "1212(b)(1)(A), as a positive amount: the person's own carryover on "
        "Schedule D line 6 plus any carryover on Schedule K-1 (Form 1041), "
        "box 11, code C, from the final year of an estate or trust, which is "
        "part of Schedule D line 5. The sum of "
        "own_short_term_capital_loss_carryover and "
        "estate_or_trust_short_term_capital_loss_carryover; an amount entered "
        "here for a year is used for that year instead, for every person in "
        "the simulation (zero for anyone it is not entered for), so enter "
        "either the sum or the leaves. Memo item: "
        "short_term_capital_gains already includes it as a loss, as Schedule "
        "D line 7 does, so it does not change gross income or the net "
        "short-term capital loss on line 6 of the 28% Rate Gain Worksheet. "
        "The Arizona property tax credit adds it back."
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
            title="2025 Instructions for Schedule D (Form 1040), Capital Loss Carryover Worksheet—Lines 6 and 14",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=10",
        ),
    ]
