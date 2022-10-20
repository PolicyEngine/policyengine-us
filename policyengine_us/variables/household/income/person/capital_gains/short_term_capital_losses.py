from policyengine_us.model_api import *


class short_term_capital_losses(Variable):
    value_type = float
    entity = Person
    label = "Short-term capital losses"
    unit = USD
    documentation = "The sum of all losses from (loss-generating) sales of assets held for one year or less."
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 1222(2)",
        href="https://www.law.cornell.edu/uscode/text/26/1222#2",
    )
