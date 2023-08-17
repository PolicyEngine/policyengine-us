from policyengine_us.model_api import *


class or_retirement_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon Retirement Income Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2022.pdf"
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        eligible = person("or_retirement_credit_eligible", period)
        # Line 1,  retirement income
        retirement_income = eligible * person("taxable_pension_income", period)
        total_retirement_income = tax_unit.sum(retirement_income)
        # Line 2, federal pension subtraction
        federal_pension_subtraction = tax_unit(
            "or_federal_pension_subtraction", period
        )
        # The retiremnt income is reduced by the amount of federal pension income
        or_taxable_pension = max_(
            total_retirement_income - federal_pension_subtraction, 0
        )
        # Line 5, total Social Security
        social_security = eligible * person("social_security", period)
        total_social_security = tax_unit.sum(social_security)
        # The base amount is reduced by the amount social security benefits received
        # (and Tier 1 RRB which are currently not modeled)
        p = (
            parameters(period)
            .gov.states["or"]
            .tax.income.credits.retirement_income
        )
        filing_status = tax_unit("filing_status", period)
        reduced_base = max_(p.base[filing_status] - total_social_security, 0)
        # Line 7, Household income
        household_income = tax_unit(
            "or_retirement_credit_household_income", period
        )
        # Line 9. line 7 - income threshold
        excess_household_income = max_(
            household_income - p.income_threshold[filing_status], 0
        )
        # The base credit is reduced by the excess household income
        base_credit = max_(0, reduced_base - excess_household_income)
        # The smaller of the pension income or the base credit will be counted
        base_or_pension = min_(or_taxable_pension, base_credit)
        # Line 11 * 9%
        return base_or_pension * p.percentage
