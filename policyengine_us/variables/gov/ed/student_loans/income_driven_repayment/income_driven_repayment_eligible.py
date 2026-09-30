from policyengine_us.model_api import *


class income_driven_repayment_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for income-driven repayment of federal student loans"
    documentation = (
        "The person has loans that the Income-Based Repayment and SAVE plans "
        "can repay and is the head or spouse of their tax unit."
    )
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(d)(1)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(d)(2)",
    )

    def formula(person, period, parameters):
        has_eligible_loans = (
            person("federal_student_loan_balance", period.this_year) > 0
        )
        # NOTE: Tax dependents are excluded because their tax unit's AGI is
        # their parents' income, not the borrower's own return.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        return has_eligible_loans & is_head_or_spouse
