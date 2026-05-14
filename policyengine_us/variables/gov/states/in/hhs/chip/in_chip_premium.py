from policyengine_us.model_api import *


class in_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana Hoosier Healthwise Package C annual premium"
    unit = USD
    documentation = (
        "Annual Indiana Hoosier Healthwise Package C (separate CHIP) "
        "premium paid by the tax unit. The state charges one rate for "
        "families with one CHIP-eligible child and a second, fixed rate "
        "for families with two or more, tiered by the tax unit's income "
        "as a fraction of the federal poverty line."
    )
    definition_period = YEAR
    defined_for = StateCode.IN
    reference = "https://www.in.gov/medicaid/members/member-programs/hhw-package-c-medworks-premium/"

    def formula(tax_unit, period, parameters):
        n_chip_children = add(tax_unit, period, ["is_chip_eligible_child"])
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states["in"].hhs.chip.premium
        rate_one = p.rate_one_child.calc(income_level)
        rate_two_plus = p.rate_two_or_more_children.calc(income_level)
        monthly = where(n_chip_children >= 2, rate_two_plus, rate_one)
        return (n_chip_children > 0) * monthly * MONTHS_IN_YEAR
