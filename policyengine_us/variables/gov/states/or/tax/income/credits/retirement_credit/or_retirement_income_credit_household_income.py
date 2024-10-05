from policyengine_us.model_api import *


class or_retirement_credit_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Household income for the Oregon Retirement Income Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/oregon-revised-statutes/title-29-revenue-and-taxation/chapter-316-personal-income-tax/additional-credits/retirement-income/section-316157-credit-for-retirement-income"
    defined_for = StateCode.OR

    adds = ["adjusted_gross_income", "tax_exempt_interest_income"]
    subtracts = ["taxable_social_security"]
