from policyengine_us.model_api import *


class net_short_term_capital_loss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net short-term capital loss"
    unit = USD
    documentation = "The excess of short-term capital losses over short-term capital gains."
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 1222(6)",
        href="https://www.law.cornell.edu/uscode/text/26/1222#6",
    )

    formula = excess(
        of="short_term_capital_losses", over="short_term_capital_gains"
    )
