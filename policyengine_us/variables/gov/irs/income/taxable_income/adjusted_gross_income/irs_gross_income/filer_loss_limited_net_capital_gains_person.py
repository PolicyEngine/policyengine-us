from policyengine_us.model_api import *


class filer_loss_limited_net_capital_gains_person(Variable):
    value_type = float
    entity = Person
    label = "Filer's loss-limited capital gains (person)"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Each head's or spouse's share of filer_loss_limited_net_capital_gains: "
        "the person's own capital gains and losses plus capital gain "
        "distributions, with a net loss of the head and spouse limited and "
        "allocated in proportion. A tax unit dependent's gains and losses are "
        "on the dependent's own return, so the dependent has none here and "
        "takes no part in the loss limit, unlike "
        "loss_limited_net_capital_gains_person."
    )
    reference = "https://www.irs.gov/pub/irs-prior/f1040sd--2025.pdf#page=2"

    def formula(person, period, parameters):
        head_or_spouse = ~person("is_tax_unit_dependent", period)
        own_gains = head_or_spouse * (
            person("capital_gains", period)
            + max_(0, person("non_sch_d_capital_gains", period))
        )
        tax_unit = person.tax_unit
        filer_gains = tax_unit.sum(own_gains)
        filer_limited = tax_unit("filer_loss_limited_net_capital_gains", period)
        proportion = np.divide(
            own_gains,
            filer_gains,
            out=np.zeros_like(own_gains),
            where=filer_gains != 0,
        )
        # With a net gain each filer keeps their own amount; with a net loss
        # the limited loss is shared in proportion to each filer's own.
        return where(filer_gains < 0, filer_limited * proportion, own_gains)
