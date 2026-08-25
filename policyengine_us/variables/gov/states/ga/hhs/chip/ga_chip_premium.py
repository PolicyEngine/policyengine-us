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
        "2024-10-01. Manual 2194 charges no premium for children under age "
        "six, children in foster care, or American Indians and Alaska "
        "Natives; the AI/AN exemption is not modeled. The state phased the "
        "2024 resumption in by renewal date - cases renewed before "
        "2024-10-01 owed no premium until their next renewal - which is "
        "not modeled, so premiums between October 2024 and September 2025 "
        "are overstated for continuing enrollees."
    )
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = "https://dch.georgia.gov/announcement/2024-08-13/peachcare-kidsr-co-payments-and-premiums-resume-oct-1-2024"

    def formula(tax_unit, period, parameters):
        # The child count is a count and the income level a ratio, so both are
        # read at the enclosing year rather than divided into monthly values.
        year = period.this_year
        person = tax_unit.members
        p = parameters(period).gov.states.ga.hhs.chip.premium
        # Manual 2194: no premium is charged for children under age six or
        # children in foster care (the AI/AN exemption is not modeled).
        charged_child = (
            person("is_chip_eligible_child", year)
            & (person("age", year) >= p.min_age)
            & ~person("is_in_foster_care", period)
        )
        n_chip_children = tax_unit.sum(charged_child)
        income_level = tax_unit("tax_unit_medicaid_income_level", year)
        per_child = p.per_child.calc(income_level)
        family_cap = p.family_cap.calc(income_level)
        return min_(n_chip_children * per_child, family_cap)
