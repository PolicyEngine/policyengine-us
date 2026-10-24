from policyengine_us.model_api import *


class repayment_assistance_plan_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Repayment Assistance Plan"
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
        # NOTE: Tax dependents are excluded because their tax unit's AGI is
        # their parents' income, not the borrower's own return.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        return p.in_effect & has_eligible_loans & is_head_or_spouse
