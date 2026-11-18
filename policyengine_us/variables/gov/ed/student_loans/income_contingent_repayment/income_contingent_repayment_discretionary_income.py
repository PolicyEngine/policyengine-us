from policyengine_us.model_api import *


class income_contingent_repayment_discretionary_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income-Contingent Repayment plan discretionary income"
    documentation = (
        "Adjusted gross income from the most recent return "
        "(income_driven_repayment_adjusted_gross_income) above the plan's "
        "multiple of the poverty guideline, per month. Joint filers combine "
        "both spouses' income; "
        "married people filing separately are in separate tax units, so only "
        "the borrower's income counts. Married borrowers who file separately "
        "but elect to repay jointly, and so combine income, are not modeled."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(4)(iii)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(1)(ii)",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.ed.student_loans.income_contingent_repayment
        agi = tax_unit(
            "income_driven_repayment_adjusted_gross_income", period.this_year
        )
        poverty_guideline = tax_unit(
            "income_driven_repayment_poverty_guideline", period.this_year
        )
        exempt_income = p.fpg_exempt_rate * poverty_guideline
        return max_(agi - exempt_income, 0) / MONTHS_IN_YEAR
