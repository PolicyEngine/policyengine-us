from policyengine_us.model_api import *


class nj_other_retirement_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey Other Retirement Income Exclusion"
    unit = USD
    documentation = "New Jersey other retirement income (Line 28b)"
    definition_period = YEAR
    reference = "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Get the pension/retirement exclusion portion of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income.exclusions.retirement

        # Pension exclusion available for household head and/or spouse if eligible based on age.
        eligible_head = tax_unit("age_head", period) >= p.age_threshold
        eligible_spouse = tax_unit("age_spouse", period) >= p.age_threshold

        # Get the total income (line 27) for head and spouse above age threshold.
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        joint = filing_status == status.JOINT
        eligible_member = (is_head * eligible_head) | (
            is_spouse * eligible_spouse * joint
        )
        gross_income = person("irs_gross_income", period)
        interest_income = person("taxable_interest_income", period)
        pension_income = person("taxable_pension_income", period)
        qualifying_income = tax_unit.sum(
            where(
                eligible_member,
                gross_income - interest_income - pension_income,
                0,
            )
        )

        # Determine income eligibility.
        income_eligible = (
            qualifying_income <= p.other_retirement_income_threshold
        )

        # Get the exclusion percentage based on filing status and income.
        # Same logic as pension/retirement exclusion.
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        exclusion_percentage = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.WIDOW,
                filing_status == status.SEPARATE,
            ],
            [
                p.percentage.single.calc(qualifying_income),
                p.percentage.joint.calc(qualifying_income),
                p.percentage.head_of_household.calc(qualifying_income),
                p.percentage.widow.calc(qualifying_income),
                p.percentage.separate.calc(qualifying_income),
            ],
        )

        # Get the potential exclusion amount for the tax unit.
        # If all the income in qualifying_income were eligible for exclusion.
        max_exclusion = qualifying_income * exclusion_percentage

        # Get the tax unit's pension/retirement exclusion from line 28a.
        pension_retirement_exclusion = tax_unit(
            "nj_pension_retirement_exclusion", period
        )

        # Get the excess (not excluded in potential/retirement) exclusion amount.
        excess = max_exclusion - pension_retirement_exclusion

        # If excess is not positive, then not eligible for other retirement exclusion.
        positive_excess = excess > 0

        # Enter the amount from line 15 (wages, salaries, tips).
        wages = person("earned_income", period)

        # Check that income from wages, business, partnership income, and corporate income are below threshold.
        earned_income_threshold = p.other_retirement_earned_income_threshold
        earned_income_eligible = wages <= earned_income_threshold

        # Calculate the final exclusion, which is the excess income after subtracting the pension/retirement exclusion.
        return (
            excess * income_eligible * positive_excess * earned_income_eligible
        )
