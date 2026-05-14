from policyengine_us.model_api import *


class al_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama ALL Kids annual enrollment fee"
    unit = USD
    documentation = (
        "Annual Alabama ALL Kids (separate CHIP) enrollment fee paid by "
        "the tax unit. Per-child fee capped at a family maximum, tiered by "
        "the tax unit's income as a fraction of the federal poverty line. "
        "The FPL tier boundaries are approximations of Alabama's "
        "dollar-based fee schedule."
    )
    definition_period = YEAR
    defined_for = StateCode.AL
    reference = "https://www.alabamapublichealth.gov/allkids/premiums-and-copays.html"

    def formula(tax_unit, period, parameters):
        n_chip_children = add(tax_unit, period, ["is_chip_eligible_child"])
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states.al.hhs.chip.enrollment_fee
        per_child = p.per_child.calc(income_level)
        family_cap = p.family_cap.calc(income_level)
        return min_(n_chip_children * per_child, family_cap)
