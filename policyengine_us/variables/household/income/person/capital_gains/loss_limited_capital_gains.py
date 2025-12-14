from policyengine_us.model_api import *


class loss_limited_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Loss-limited capital gains (person's share)"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Capital gains with federal capital loss limitation applied. "
        "This allocates the tax unit's loss_limited_net_capital_gains "
        "proportionally to each person based on their share of total "
        "capital gains/losses."
    )
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f1040sd.pdf "
        "Federal Schedule D limits capital losses to $3,000 ($1,500 if married filing separately). "
        "States that use federal AGI or federal Schedule D amounts should use this variable."
    )

    def formula(person, period, parameters):
        # Get person's raw capital gains
        person_capital_gains = person("capital_gains", period)

        # Get tax unit totals
        tax_unit = person.tax_unit
        tax_unit_capital_gains = tax_unit.sum(person_capital_gains)
        tax_unit_loss_limited = tax_unit(
            "loss_limited_net_capital_gains", period
        )

        # If no capital gains in the tax unit, return 0
        # If gains (positive), each person keeps their full amount
        # If losses, allocate the loss-limited amount proportionally
        is_loss = tax_unit_capital_gains < 0

        # Calculate each person's proportion of the tax unit's capital gains
        # Avoid division by zero
        proportion = where(
            tax_unit_capital_gains != 0,
            person_capital_gains / tax_unit_capital_gains,
            0,
        )

        # For losses: allocate loss_limited amount proportionally
        # For gains or zero: return person's original capital gains
        return where(
            is_loss,
            tax_unit_loss_limited * proportion,
            person_capital_gains,
        )
