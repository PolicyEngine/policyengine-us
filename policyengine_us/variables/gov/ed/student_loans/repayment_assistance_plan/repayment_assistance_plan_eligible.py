from policyengine_us.model_api import *


class repayment_assistance_plan_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Repayment Assistance Plan"
    documentation = (
        "The person has loans that the Repayment Assistance Plan can repay, "
        "is the head or spouse of their tax unit, and the plan is in effect "
        "(from July 1, 2026). Modeling restriction: a borrower claimed as "
        "someone else's tax dependent is treated as ineligible and owes $0, "
        "because their tax unit's adjusted gross income is the claiming "
        "taxpayer's, not the borrower's own. The law does not exclude these "
        "borrowers (34 CFR 685.209(c)(6)): their base payment would come from "
        "their own income, and the $10 minimum payment would apply."
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
        # Modeling restriction: tax dependents are excluded (see documentation
        # and rulespec-us#1455 companion case C17).
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        return p.in_effect & has_eligible_loans & is_head_or_spouse
