from policyengine_us.model_api import *


class il_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois All Kids annual premium"
    unit = USD
    documentation = (
        "Annual Illinois All Kids premium paid by the tax unit. Per-child "
        "monthly premium capped at a family maximum, tiered by the tax "
        "unit's income as a fraction of the federal poverty line. Only "
        "applies to families whose children qualify for All Kids Premium "
        "Level 1 or Level 2; lower-income bands (Assist, Share) charge no "
        "premium."
    )
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://hfs.illinois.gov/medicalprograms/allkids/income.html"

    def formula(tax_unit, period, parameters):
        n_chip_children = add(tax_unit, period, ["is_chip_eligible_child"])
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states.il.hhs.chip.premium
        per_child = p.per_child.calc(income_level)
        family_cap = p.family_cap.calc(income_level)
        monthly = min_(n_chip_children * per_child, family_cap)
        return monthly * MONTHS_IN_YEAR
