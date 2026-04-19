from policyengine_us.model_api import *


class ks_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas KanCare annual CHIP premium"
    unit = USD
    documentation = (
        "Annual Kansas KanCare separate CHIP premium paid by the tax unit. "
        "One flat monthly premium covers all CHIP-eligible children, tiered "
        "by the tax unit's income as a fraction of the federal poverty line."
    )
    definition_period = YEAR
    defined_for = StateCode.KS
    reference = "https://klrd.gov/2026/03/02/briefing-book-2026-childrens-eligibility-for-chip-mchip-medicaid-and-hcbs-including-information-on-premium-requirements-for-chip/"

    def formula(tax_unit, period, parameters):
        has_chip_member = add(tax_unit, period, ["is_chip_eligible"]) > 0
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states.ks.hhs.chip
        return has_chip_member * p.premium.calc(income_level) * MONTHS_IN_YEAR
