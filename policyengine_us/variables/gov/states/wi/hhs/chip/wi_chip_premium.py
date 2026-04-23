from policyengine_us.model_api import *


class wi_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin BadgerCare Plus annual CHIP premium"
    unit = USD
    documentation = (
        "Annual Wisconsin BadgerCare Plus premium paid by the tax unit for "
        "CHIP-eligible children. Per-child monthly premium with no explicit "
        "family cap, but the state applies the federal 5 percent of income "
        "cost-sharing cap at the assistance-group level. Tiered by the tax "
        "unit's income as a fraction of the federal poverty line."
    )
    definition_period = YEAR
    defined_for = StateCode.WI
    reference = "https://www.emhandbooks.wisconsin.gov/bcplus/policyfiles/6/48.1.htm"

    def formula(tax_unit, period, parameters):
        n_chip_children = add(tax_unit, period, ["is_chip_eligible_child"])
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states.wi.hhs.chip.premium
        per_child = p.per_child.calc(income_level)
        return n_chip_children * per_child * MONTHS_IN_YEAR
