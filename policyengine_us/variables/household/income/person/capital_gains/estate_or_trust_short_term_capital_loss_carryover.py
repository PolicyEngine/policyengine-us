from policyengine_us.model_api import *


class estate_or_trust_short_term_capital_loss_carryover(Variable):
    value_type = float
    entity = Person
    label = "Short-term capital loss carryover from a terminated estate or trust"
    unit = USD
    documentation = (
        "Short-term capital loss carryover a beneficiary succeeds to when an "
        "estate or trust terminates, as a positive amount: Schedule K-1 (Form "
        "1041), box 11, code C, from the estate or trust's final year. Under "
        "26 U.S.C. 642(h)(1) and Reg. 1.642(h)-1(a), a capital loss carryover "
        "the estate or trust could have used after that year but for the "
        "termination is allowed to the beneficiaries succeeding to its "
        "property. Reg. 1.642(h)-1(b) keeps it short-term. The beneficiary "
        "reports it on Schedule D line 5. The person's own carryover goes in "
        "own_short_term_capital_loss_carryover instead. Memo item: "
        "short_term_capital_gains already includes it as a loss, as Schedule "
        "D line 7 does. Zero unless entered."
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.short_term_capital_gains"
    reference = [
        dict(
            title="26 U.S. Code § 642(h)(1)",
            href="https://www.law.cornell.edu/uscode/text/26/642#h_1",
        ),
        dict(
            title="26 CFR § 1.642(h)-1",
            href="https://www.law.cornell.edu/cfr/text/26/1.642(h)-1",
        ),
        dict(
            title="2025 Instructions for Schedule K-1 (Form 1041) for a Beneficiary Filing Form 1040 or 1040-SR, Box 11, Codes C and D",
            href="https://www.irs.gov/pub/irs-prior/i1041sk1--2025.pdf#page=3",
        ),
    ]
