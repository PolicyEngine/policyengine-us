from openfisca_us.model_api import *


class net_long_term_capital_loss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net long-term capital loss"
    unit = USD
    documentation = (
        "The excess of long-term capital losses over long-term capital gains."
    )
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 1222(8)",
        href="https://www.law.cornell.edu/uscode/text/26/1222#8",
    )

    formula = excess(
        of="long_term_capital_losses", over="long_term_capital_gains"
    )
