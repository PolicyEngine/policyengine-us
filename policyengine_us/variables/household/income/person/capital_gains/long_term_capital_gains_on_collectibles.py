from policyengine_us.model_api import *


class long_term_capital_gains_on_collectibles(Variable):
    value_type = float
    entity = Person
    label = "Long-term capital gains on collectibles"
    unit = USD
    documentation = "The sum of all gains on collectibles made from (profitable) sales of assets held for more than one year."
    definition_period = YEAR
    reference = dict(
        title="IRS Topic No. 409 Capital Gains and Losses",
        href="https://www.irs.gov/taxtopics/tc409",
    )
