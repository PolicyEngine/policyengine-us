from policyengine_us.model_api import *


class gambling_losses(Variable):
    value_type = float
    entity = Person
    label = "Gambling losses"
    unit = USD
    documentation = (
        "Losses from wagering transactions of a person who does not gamble "
        "as a trade or business, such as the cost of losing bets and of "
        "non-winning lottery and raffle tickets (Schedule A (Form 1040) "
        "line 16), before any limit. This input does not separate losses "
        "by where the wager was placed, so state rules that depend on it "
        "(a state lottery, in-state licensed gaming) are not modeled."
    )
    definition_period = YEAR
    reference = "https://www.irs.gov/pub/irs-prior/i1040sca--2024.pdf#page=11"
