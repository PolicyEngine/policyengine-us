from policyengine_us.model_api import *


class la_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana LaCHIP annual premium"
    unit = USD
    documentation = (
        "Annual Louisiana LaCHIP premium paid by the tax unit. Regular "
        "LaCHIP has no premium; only the LaCHIP Affordable Plan tier "
        "(above 212 percent FPL) charges a flat monthly household premium."
    )
    definition_period = YEAR
    defined_for = StateCode.LA
    reference = "https://ldh.la.gov/faq/category/19"

    def formula(tax_unit, period, parameters):
        has_chip_member = add(tax_unit, period, ["is_chip_eligible"]) > 0
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        p = parameters(period).gov.states.la.hhs.chip
        return has_chip_member * p.premium.calc(income_level) * MONTHS_IN_YEAR
