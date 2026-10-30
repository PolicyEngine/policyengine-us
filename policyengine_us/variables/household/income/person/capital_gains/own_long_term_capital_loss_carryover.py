from policyengine_us.model_api import *


class own_long_term_capital_loss_carryover(Variable):
    value_type = float
    entity = Person
    label = "Own long-term capital loss carryover"
    unit = USD
    documentation = (
        "Long-term capital loss carried to the year from the person's own "
        "earlier years under 26 U.S.C. 1212(b)(1)(B), as a positive amount: "
        "Schedule D line 14, from line 13 of the Capital Loss Carryover "
        "Worksheet. A carryover from a terminated estate or trust goes in "
        "estate_or_trust_long_term_capital_loss_carryover instead. Memo item: "
        "long_term_capital_gains already includes it as a loss, as Schedule D "
        "line 15 does. Zero, no carryover, unless entered."
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.long_term_capital_gains"
    reference = [
        dict(
            title="26 U.S. Code § 1212(b)(1)(B)",
            href="https://www.law.cornell.edu/uscode/text/26/1212#b_1_B",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), Capital Loss Carryover Worksheet—Lines 6 and 14",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=10",
        ),
    ]
