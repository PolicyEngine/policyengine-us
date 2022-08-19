from openfisca_us.model_api import *


class net_short_term_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net short-term capital gain"
    unit = USD
    documentation = "The excess of short-term capital gains over short-term capital losses."
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 1222(5)",
        href="https://www.law.cornell.edu/uscode/text/26/1222#5",
    )

    formula = excess(
        of="short_term_capital_gains", over="short_term_capital_losses"
    )
