from policyengine_us.model_api import *


class loss_limited_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Loss-limited capital gains"
    unit = USD
    definition_period = YEAR
    reference = "https://www.irs.gov/pub/irs-pdf/f1040sd.pdf"

    def formula(person, period, parameters):
        # Get person's raw capital gains
        person_capital_gains = person("capital_gains", period)

        # Get tax unit totals
        tax_unit = person.tax_unit
        tax_unit_capital_gains = tax_unit.sum(person_capital_gains)
        tax_unit_loss_limited = tax_unit(
            "loss_limited_net_capital_gains", period
        )

        # If net gains (positive), return person's share unchanged
        # If net losses, allocate the loss-limited amount proportionally
        is_loss = tax_unit_capital_gains < 0

        # For losses: allocate loss_limited amount proportionally
        proportion = where(
            tax_unit_capital_gains != 0,
            person_capital_gains / tax_unit_capital_gains,
            0,
        )

        return where(
            is_loss,
            tax_unit_loss_limited * proportion,
            person_capital_gains,
        )
