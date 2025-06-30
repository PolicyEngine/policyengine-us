from policyengine_us.model_api import *


class or_retirement_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon Retirement Income Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2021.pdf#page=108"
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        # follows twelve-line worksheet on page 108 of above reference

        # Line 1, retirement income
        person = tax_unit.members
        eligible = person("or_retirement_credit_eligible_person", period)
        retirement_income = eligible * person("taxable_pension_income", period)
        total_retirement_income = tax_unit.sum(retirement_income)

        # Line 2, federal pension subtraction
        federal_pension_subtraction = tax_unit(
            "or_federal_pension_subtraction", period
        )

        # Line 3, retirement income reduced by federal pension subtraction
        or_taxable_pension = max_(
            0, total_retirement_income - federal_pension_subtraction
        )

        # Line 5, total social security
        social_security = add(tax_unit, period, ["social_security"])

        # Line 6, base amount reduced by social security benefits received
        p = (
            parameters(period)
            .gov.states["or"]
            .tax.income.credits.retirement_income
        )
        filing_status = tax_unit("filing_status", period)
        reduced_base = max_(0, p.base[filing_status] - social_security)

        # Line 7, household income
        household_income = tax_unit(
            "or_retirement_credit_household_income", period
        )

        # Line 9, household income minus income threshold
        excess_household_income = max_(
            0, household_income - p.income_threshold[filing_status]
        )

        # Line 10, reduced base amount is reduced by excess household income
        base_amount = max_(0, reduced_base - excess_household_income)

        # Line 11, calculate credit
        return min_(or_taxable_pension, base_amount) * p.percentage
