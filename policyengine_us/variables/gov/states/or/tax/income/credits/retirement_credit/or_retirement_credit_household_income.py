from policyengine_us.model_api import *


class or_retirement_credit_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Household income for the Oregon Retirement Income Tax Credit"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Federal AGI plus tax-exempt interest, less the Social Security "
        "benefits AGI holds. ORS 316.157(2)(b) leaves Social Security "
        "benefits out of household income, and (2)(f) defines them as "
        "section 86 benefits: title II benefits and tier 1 railroad "
        "retirement benefits."
    )
    reference = (
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html"  # ORS 316.157
    )
    defined_for = StateCode.OR

    adds = ["adjusted_gross_income", "tax_exempt_interest_income"]
    subtracts = [
        "taxable_social_security",
        "taxable_railroad_social_security_equivalent_benefits",
    ]
