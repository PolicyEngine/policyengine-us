from policyengine_us.model_api import *


class ma_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Massachusetts MassHealth annual CHIP premium"
    unit = USD
    documentation = (
        "Annual Massachusetts MassHealth (combination M-CHIP/S-CHIP) "
        "premium paid by the tax unit for CHIP-eligible children. Per-child "
        "monthly premium capped at a three-child family maximum, tiered by "
        "the tax unit's income as a fraction of the federal poverty line."
    )
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.law.cornell.edu/regulations/massachusetts/130-CMR-506-011"

    def formula(tax_unit, period, parameters):
        n_chip_children = add(tax_unit, period, ["is_chip_eligible_child"])
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states.ma.hhs.chip.premium
        per_child = p.per_child.calc(income_level)
        family_cap = p.family_cap.calc(income_level)
        monthly = min_(n_chip_children * per_child, family_cap)
        return monthly * MONTHS_IN_YEAR
