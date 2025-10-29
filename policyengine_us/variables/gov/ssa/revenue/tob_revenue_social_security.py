from policyengine_us.model_api import *


class tob_revenue_social_security(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Social Security TOB revenue"
    documentation = "Tax revenue from tier 1 Social Security benefit taxation credited to OASDI trust funds"
    unit = USD

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.social_security.taxability.revenue_allocation
        tier_1 = tax_unit("taxable_social_security_tier_1", period)

        # Calculate effective tax rate
        income_tax = tax_unit("income_tax_before_credits", period)
        taxable_income = tax_unit("taxable_income", period)
        effective_rate = where(
            taxable_income > 0, income_tax / taxable_income, 0
        )

        # Apply allocation parameter
        return tier_1 * effective_rate * p.tier_1_to_oasdi
