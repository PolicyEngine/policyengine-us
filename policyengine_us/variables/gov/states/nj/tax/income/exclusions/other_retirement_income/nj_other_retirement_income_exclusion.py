from policyengine_us.model_api import *


class nj_other_retirement_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey Other Retirement Income Exclusion"
    unit = USD
    documentation = "New Jersey other retirement income (Line 28b)"
    definition_period = YEAR
    reference = (
        "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21",
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-6-15/",
    )
    defined_for = "nj_other_retirement_income_exclusion_eligible"

    def formula(tax_unit, period, parameters):
        # Get the pension/retirement exclusion portion of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income.exclusions.retirement

        # Get the qualifying tax unit income for this exclusion.
        qualifying_income = tax_unit(
            "nj_other_retirement_income_exclusion_qualifying_income", period
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

        # Get the potential exclusion amount for the tax unit
        # if all the income in qualifying_income were eligible for exclusion.
        max_exclusion = qualifying_income * exclusion_percentage

        # Get the tax unit's pension/retirement exclusion from line 28a.
        pension_retirement_exclusion = tax_unit(
            "nj_pension_retirement_exclusion", period
        )

        # Get the excess (not excluded in potential/retirement) exclusion amount.
        excess = max_exclusion - pension_retirement_exclusion

        # Calculate the final exclusion, which is the excess income after subtracting the pension/retirement exclusion.
        # If excess is not positive, then no exclusion.
        return max_(0, excess)
