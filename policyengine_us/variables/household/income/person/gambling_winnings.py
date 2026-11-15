from policyengine_us.model_api import *


class gambling_winnings(Variable):
    value_type = float
    entity = Person
    label = "Gambling winnings"
    unit = USD
    documentation = (
        "Gambling winnings of a person who does not gamble as a trade or "
        "business, as reported on Schedule 1 (Form 1040) line 8b: the full "
        "winnings, including lottery and raffle prizes, not reduced by "
        "losses. This input does not separate winnings by source or by "
        "prize, so state rules that depend on them (a state's own lottery, "
        "prizes under a threshold, noncash prizes) are not modeled."
    )
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-prior/f1040s1--2024.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=91",
    )
