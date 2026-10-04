from policyengine_us.model_api import *


class loss_limited_net_capital_gains_person(Variable):
    value_type = float
    entity = Person
    label = "Loss-limited capital gains (person)"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Each person's share of loss_limited_net_capital_gains: the person's "
        "capital gains and losses plus capital gain distributions, with a "
        "tax-unit net loss limited and allocated in proportion."
    )
    reference = "https://www.irs.gov/pub/irs-prior/f1040sd--2025.pdf#page=2"

    def formula(person, period, parameters):
        # The person's capital gains and losses, plus capital gain
        # distributions, which go on Schedule D line 13 with them.
        person_capital_gains = add(
            person, period, ["capital_gains", "non_sch_d_capital_gains"]
        )

        # Get tax unit totals
        tax_unit = person.tax_unit
        tax_unit_capital_gains = tax_unit.sum(person_capital_gains)
        tax_unit_loss_limited = tax_unit("loss_limited_net_capital_gains", period)

        # If net gains (positive), return person's share unchanged
        # If net losses, allocate the loss-limited amount proportionally
        is_loss = tax_unit_capital_gains < 0

        # For losses: allocate loss_limited amount proportionally.
        # Use np.divide with mask to avoid divide-by-zero warnings.
        mask = tax_unit_capital_gains != 0
        proportion = np.divide(
            person_capital_gains,
            tax_unit_capital_gains,
            out=np.zeros_like(person_capital_gains),
            where=mask,
        )

        return where(
            is_loss,
            tax_unit_loss_limited * proportion,
            person_capital_gains,
        )
