from openfisca_us.model_api import *


class net_long_term_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net long-term capital gain"
    unit = USD
    documentation = (
        "The excess of long-term capital gains over long-term capital losses."
    )
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 1222(7)",
        href="https://www.law.cornell.edu/uscode/text/26/1222#7",
    )

    formula = excess(
        of="long_term_capital_gains", over="long_term_capital_losses"
    )
