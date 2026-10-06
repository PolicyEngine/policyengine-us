from policyengine_us.model_api import *


class filer_loss_limited_net_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Filer's loss-limited net capital gains"
    unit = USD
    documentation = (
        "Form 1040 line 7a of the head and spouse: their Schedule D net "
        "capital gain or loss, including capital gain distributions (line "
        "13), with a net loss limited under 26 USC 1211(b). This is Form 8960 "
        "line 5a without Schedule 1 line 4. A tax unit dependent's gains and "
        "losses are on the dependent's own return. Unlike "
        "loss_limited_net_capital_gains, this leaves dependents out."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1211#b",
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=7",
        "https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs
        filing_status = tax_unit("filing_status", period)
        loss_limit = p.capital_gains.loss_limit[filing_status]
        # net_capital_gains sums every member's Schedule D gains and losses,
        # or holds a tax unit amount supplied as an input. A tax unit
        # dependent's own gains and losses are on the dependent's return, so
        # they come out here; a supplied amount is kept.
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        dependent_gains = tax_unit.sum(
            dependent
            * (
                person("long_term_capital_gains", period)
                + person("short_term_capital_gains", period)
            )
        )
        net_capital_gains = tax_unit("net_capital_gains", period) - dependent_gains
        # Capital gain distributions go on Schedule D line 13 with the other
        # gains and losses, so they net before the limit. Each filer's input
        # is floored at zero, as in irs_gross_income.
        not_dependent = ~dependent
        distributions = tax_unit.sum(
            not_dependent * max_(0, person("non_sch_d_capital_gains", period))
        )
        return max_(-loss_limit, net_capital_gains + distributions)
