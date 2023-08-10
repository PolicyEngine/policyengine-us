from policyengine_us.model_api import *


class nj_other_retirement_income_exclusion_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New Jersey Other Retirement Income Exclusion Eligible"
    unit = USD
    documentation = "New Jersey other retirement income eligible"
    definition_period = YEAR
    reference = (
        "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21",
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-6-15/",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Get the pension/retirement exclusion portion of the parameter tree.
        p = parameters(
            period
        ).gov.states.nj.tax.income.exclusions.retirement.other_retirement_income

        # Get the qualifying tax unit income for this exclusion.
        qualifying_income = tax_unit(
            "nj_other_retirement_income_exclusion_qualifying_income", period
        )

        # Determine income eligibility.
        income_eligible = qualifying_income <= p.income_threshold

        # Enter the amount from line 15 (wages, salaries, tips).
        wages = add(tax_unit, period, ["earned_income"])

        # Check that income from wages, business, partnership income, and corporate income are below threshold.
        earned_income_threshold = p.earned_income_threshold
        earned_income_eligible = wages <= earned_income_threshold

        # Calculate the final exclusion, which is the excess income after subtracting the pension/retirement exclusion.
        return income_eligible * earned_income_eligible
