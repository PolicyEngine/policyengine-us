from policyengine_us.model_api import *


class is_ptc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Premium Tax Credit eligible"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        eligibility = parameters(
            period
        ).gov.irs.credits.premium_tax_credit.eligibility
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        on_marketplace = (
            add(tax_unit, period, ["has_marketplace_health_coverage"]) > 0
        )
        return on_marketplace & eligibility.calc(income_level)
