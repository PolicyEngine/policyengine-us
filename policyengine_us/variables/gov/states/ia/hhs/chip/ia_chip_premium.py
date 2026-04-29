from policyengine_us.model_api import *


class ia_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa Hawki annual premium"
    unit = USD
    documentation = (
        "Annual Iowa Hawki (separate CHIP) premium paid by the tax unit. "
        "Per-child monthly premium capped at a family maximum, tiered by "
        "the tax unit's income as a fraction of the federal poverty line."
    )
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = "https://hhs.iowa.gov/media/10189/download?inline="

    def formula(tax_unit, period, parameters):
        n_chip_children = add(tax_unit, period, ["is_chip_eligible_child"])
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states.ia.hhs.chip.premium
        per_child = p.per_child.calc(income_level)
        family_cap = p.family_cap.calc(income_level)
        monthly = min_(n_chip_children * per_child, family_cap)
        return monthly * MONTHS_IN_YEAR
