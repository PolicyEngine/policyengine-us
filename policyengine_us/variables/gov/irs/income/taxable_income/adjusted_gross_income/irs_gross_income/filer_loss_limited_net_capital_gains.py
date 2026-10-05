from policyengine_us.model_api import *


class filer_loss_limited_net_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Filer's loss-limited net capital gains"
    unit = USD
    documentation = (
        "Schedule D net capital gain or loss of the head and spouse, with a "
        "net loss limited under 26 USC 1211(b): the Schedule D part of Form "
        "8960 line 5a. A tax unit dependent's gains and losses are on the "
        "dependent's own return. Unlike loss_limited_net_capital_gains, this "
        "leaves dependents out."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1211#b",
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=7",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs
        filing_status = tax_unit("filing_status", period)
        loss_limit = p.capital_gains.loss_limit[filing_status]
        net_capital_gains = tax_unit_non_dep_add(
            tax_unit, period, ["long_term_capital_gains", "short_term_capital_gains"]
        )
        return max_(-loss_limit, net_capital_gains)
