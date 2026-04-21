from policyengine_us.model_api import *


class fl_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Florida KidCare annual premium"
    unit = USD
    documentation = (
        "Annual Florida KidCare (separate CHIP) premium paid by the tax "
        "unit. One flat monthly premium covers all CHIP-eligible children, "
        "tiered by the tax unit's income as a fraction of the federal "
        "poverty line."
    )
    definition_period = YEAR
    defined_for = StateCode.FL
    reference = (
        "https://floridakidcare.org/docs/cost/florida_kidcare_income_guidelines.pdf"
    )

    def formula(tax_unit, period, parameters):
        has_chip_member = add(tax_unit, period, ["is_chip_eligible"]) > 0
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states.fl.hhs.chip
        return has_chip_member * p.premium.calc(income_level) * MONTHS_IN_YEAR
