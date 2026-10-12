from policyengine_us.model_api import *


class long_term_capital_gains_on_collectibles(Variable):
    value_type = float
    entity = Person
    label = "Long-term capital gains on collectibles"
    unit = USD
    documentation = (
        "The collectibles part of the 28-percent rate gain as reported on "
        "Schedule D line 18: already net of collectibles loss, the net "
        "short-term capital loss and the long-term capital loss carryover, "
        "so the model does not net it again. The microdata carry it from "
        "the PUF's Schedule D line 18. Enter a collectibles gain or loss "
        "before that netting as collectibles_gain_or_loss instead. Memo item: "
        "long_term_capital_gains already includes it."
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.long_term_capital_gains"
    reference = [
        dict(
            title="26 U.S. Code § 1(h)(4)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_4",
        ),
        dict(
            title="2025 Instructions for Schedule D (Form 1040), 28% Rate Gain Worksheet—Line 18",
            href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=11",
        ),
    ]
