from policyengine_us.model_api import *


class id_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho CHIP annual premium"
    unit = USD
    documentation = (
        "Annual Idaho CHIP premium paid by the tax unit. Per-child monthly "
        "premium with no family cap, tiered by the tax unit's income as a "
        "fraction of the federal poverty line."
    )
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = "https://www.medicaid.gov/CHIP/Downloads/ID/IDCurrentFactsheet.pdf"

    def formula(tax_unit, period, parameters):
        n_chip_children = add(tax_unit, period, ["is_chip_eligible_child"])
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states.id.hhs.chip.premium
        per_child = p.per_child.calc(income_level)
        return n_chip_children * per_child * MONTHS_IN_YEAR
