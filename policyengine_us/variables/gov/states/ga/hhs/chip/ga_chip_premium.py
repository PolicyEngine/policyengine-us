from policyengine_us.model_api import *


class ga_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia PeachCare for Kids monthly premium"
    unit = USD
    documentation = (
        "Monthly Georgia PeachCare for Kids (separate CHIP) premium paid by "
        "the tax unit. Per-child monthly premium capped at a family maximum, "
        "tiered by the tax unit's income as a fraction of the federal "
        "poverty line. Defined monthly because premiums resumed mid-year, on "
        "2024-10-01."
    )
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = "https://dch.georgia.gov/announcement/2024-08-13/peachcare-kidsr-co-payments-and-premiums-resume-oct-1-2024"

    def formula(tax_unit, period, parameters):
        # The child count is a count and the income level a ratio, so both are
        # read at the enclosing year rather than divided into monthly values.
        year = period.this_year
        n_chip_children = add(tax_unit, year, ["is_chip_eligible_child"])
        income_level = tax_unit("tax_unit_medicaid_income_level", year)
        p = parameters(period).gov.states.ga.hhs.chip.premium
        per_child = p.per_child.calc(income_level)
        family_cap = p.family_cap.calc(income_level)
        return min_(n_chip_children * per_child, family_cap)
