from policyengine_us.model_api import *


class ny_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York Child Health Plus monthly premium"
    unit = USD
    documentation = (
        "Monthly New York Child Health Plus (separate CHIP) premium paid by "
        "the tax unit. Subsidized per-child monthly premiums are capped at "
        "a three-child family maximum and tiered by the tax unit's income "
        "as a fraction of the federal poverty line. Families above 400 "
        "percent FPL pay an uncapped statewide average full plan premium, "
        "because the actual premium varies by health plan. Defined monthly "
        "because schedule changes take effect mid-year, most recently the "
        "October 2022 restructuring under SPA NY-22-0033."
    )
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = "https://www.health.ny.gov/health_care/child_health_plus/eligibility_and_cost.htm"

    def formula(tax_unit, period, parameters):
        # The child count is a count and the income level a ratio, so both are
        # read at the enclosing year rather than divided into monthly values.
        year = period.this_year
        n_chip_children = add(tax_unit, year, ["is_chip_eligible_child"])
        income_level = tax_unit("tax_unit_medicaid_income_level", year)
        p = parameters(period).gov.states.ny.hhs.chip.premium
        per_child = p.per_child.calc(income_level)
        family_cap = p.family_cap.calc(income_level)
        return min_(n_chip_children * per_child, family_cap)
