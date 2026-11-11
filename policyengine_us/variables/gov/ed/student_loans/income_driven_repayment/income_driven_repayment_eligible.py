from policyengine_us.model_api import *


class income_driven_repayment_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for income-driven repayment of federal student loans"
    documentation = (
        "The person has loans that the Income-Based Repayment, SAVE, Pay As "
        "You Earn and Income-Contingent Repayment plans can repay. A borrower "
        "whom another taxpayer claims as a dependent is eligible like any "
        "other: 34 CFR 685.209(c)(2)-(5) do not exclude them. Their payment "
        "comes from their own income "
        "(income_driven_repayment_dependent_adjusted_gross_income) and a "
        "family of one, not from the claiming taxpayer's return."
    )
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(c)(3)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(c)(4)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(c)(5)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(d)(1)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(d)(2)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(d)(3)",
    )

    def formula(person, period, parameters):
        return person("federal_student_loan_balance", period.this_year) > 0
