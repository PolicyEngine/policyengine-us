from policyengine_us.model_api import *


class ny_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York Child Health Plus annual premium"
    unit = USD
    documentation = (
        "Annual New York Child Health Plus (separate CHIP) premium paid by "
        "the tax unit. Per-child monthly premium capped at a three-child "
        "family maximum, tiered by the tax unit's income as a fraction of "
        "the federal poverty line. Families above 400 percent FPL pay the "
        "full plan cost, which varies by health plan and is not modeled."
    )
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = "https://www.health.ny.gov/health_care/child_health_plus/eligibility_and_cost.htm"

    def formula(tax_unit, period, parameters):
        n_chip_children = add(tax_unit, period, ["is_chip_eligible_child"])
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states.ny.hhs.chip.premium
        per_child = p.per_child.calc(income_level)
        family_cap = p.family_cap.calc(income_level)
        monthly = min_(n_chip_children * per_child, family_cap)
        return monthly * MONTHS_IN_YEAR
