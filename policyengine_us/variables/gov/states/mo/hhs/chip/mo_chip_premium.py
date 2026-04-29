from policyengine_us.model_api import *


class mo_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri MO HealthNet for Kids annual CHIP premium"
    unit = USD
    documentation = (
        "Annual Missouri MO HealthNet for Kids (separate CHIP) premium "
        "paid by the tax unit. The state sets one household-level monthly "
        "premium that varies by both family size and three FPL tiers "
        "(above 150, above 185, and above 225 percent FPL)."
    )
    definition_period = YEAR
    defined_for = StateCode.MO
    reference = (
        "https://mydss.mo.gov/childrens-health-insurance-program-chip-premium-chart"
    )

    def formula(tax_unit, period, parameters):
        has_chip_member = add(tax_unit, period, ["is_chip_eligible"]) > 0
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        family_size = tax_unit("tax_unit_size", period)
        p = parameters(period).gov.states.mo.hhs.chip.premium
        tier_1 = p.tier_1.calc(family_size)
        tier_2 = p.tier_2.calc(family_size)
        tier_3 = p.tier_3.calc(family_size)
        monthly = select(
            [income_level > 2.25, income_level > 1.85, income_level > 1.50],
            [tier_3, tier_2, tier_1],
            default=0,
        )
        return has_chip_member * monthly * MONTHS_IN_YEAR
