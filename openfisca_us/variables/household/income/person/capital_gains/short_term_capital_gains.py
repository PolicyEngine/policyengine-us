from openfisca_us.model_api import *


class short_term_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Short-term capital gains"
    unit = USD
    documentation = "The sum of all gains made from (profitable) sales of assets held for one year or less."
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 1222(1)",
        href="https://www.law.cornell.edu/uscode/text/26/1222#1",
    )
