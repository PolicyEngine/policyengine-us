from policyengine_us.model_api import *


class save_plan_discretionary_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "SAVE plan discretionary income"
    documentation = (
        "Adjusted gross income above the plan's multiple of the poverty "
        "guideline, per month. Joint filers combine both spouses' income; "
        "married people filing separately are in separate tax units, so only "
        "the borrower's income counts."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(4)(i)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(1)(i)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(1)",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.ed.student_loans.save_plan
        agi = tax_unit("adjusted_gross_income", period.this_year)
        poverty_guideline = tax_unit(
            "income_driven_repayment_poverty_guideline", period.this_year
        )
        exempt_income = p.fpg_exempt_rate * poverty_guideline
        return max_(agi - exempt_income, 0) / MONTHS_IN_YEAR
