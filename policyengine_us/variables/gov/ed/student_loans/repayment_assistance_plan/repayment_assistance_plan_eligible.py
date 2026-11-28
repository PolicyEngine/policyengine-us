from policyengine_us.model_api import *


class repayment_assistance_plan_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Repayment Assistance Plan"
    documentation = (
        "The person has loans that the Repayment Assistance Plan can repay "
        "and the plan is in effect (from July 1, 2026). A borrower whom "
        "another taxpayer claims as a dependent is eligible like any other: "
        "34 CFR 685.209(c)(6) lets any Direct Loan borrower with eligible "
        "loans repay under the plan. Their base payment comes from their own "
        "income (income_driven_repayment_dependent_adjusted_gross_income), "
        "and the $10 minimum payment applies."
    )
    definition_period = MONTH
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(c)(6)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(d)(4)",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans.repayment_assistance_plan
        has_eligible_loans = (
            person("federal_student_loan_balance", period.this_year) > 0
        )
        return p.in_effect & has_eligible_loans
