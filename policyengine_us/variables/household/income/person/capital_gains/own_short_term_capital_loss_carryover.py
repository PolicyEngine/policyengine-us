from policyengine_us.model_api import *


class own_short_term_capital_loss_carryover(Variable):
    value_type = float
    entity = Person
    label = "Own short-term capital loss carryover"
    unit = USD
    documentation = (
        "Short-term capital loss carried to the year from the person's own "
        "earlier years under 26 U.S.C. 1212(b)(1)(A), as a positive amount: "
        "Schedule D line 6, from line 8 of the Capital Loss Carryover "
        "Worksheet. A carryover from a terminated estate or trust goes in "
        "estate_or_trust_short_term_capital_loss_carryover instead. Memo item: "
        "short_term_capital_gains already includes it as a loss, as Schedule D "
        "line 7 does. Zero, no carryover, unless entered."
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.short_term_capital_gains"
    reference = [
        dict(
            title="26 U.S. Code § 1212(b)(1)(A)",
            href="https://www.law.cornell.edu/uscode/text/26/1212#b_1_A",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), Capital Loss Carryover Worksheet—Lines 6 and 14",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=10",
        ),
    ]
