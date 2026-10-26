from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.student_loans.student_loan_amortization_helpers import (
    amortized_monthly_payment,
)


class parent_plus_standard_repayment_payment(Variable):
    value_type = float
    entity = Person
    label = "Parent PLUS standard repayment plan monthly payment"
    documentation = (
        "Fixed monthly payment that repays the person's parent PLUS loans "
        "(federal_parent_plus_loan_balance) over the 10-year standard "
        "repayment plan, which covers Direct PLUS Loan borrowers, parents "
        "included. The balance is amortized at the person's "
        "federal_student_loan_interest_rate, a single rate for all of their "
        "federal loans, and the payment is at least the plan minimum and no "
        "more than the balance. It assumes the borrower is in active "
        "repayment. This is separate from standard_repayment_payment, so the "
        "income-driven repayment caps stay on the loans those plans can "
        "repay. Parent PLUS loans made on or after July 1, 2026, which repay "
        "under the tiered standard plan, are not modeled here, nor is "
        "repayment of consolidated parent PLUS loans under the "
        "Income-Contingent Repayment plan."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(1)",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans.standard_repayment
        balance = person("federal_parent_plus_loan_balance", period.this_year)
        annual_rate = person("federal_student_loan_interest_rate", period.this_year)
        number_of_payments = p.repayment_period * MONTHS_IN_YEAR
        amortized_payment = amortized_monthly_payment(
            balance, annual_rate, number_of_payments
        )
        # As in standard_repayment_payment, the minimum does not apply to a
        # final payment below it.
        return min_(max_(amortized_payment, p.minimum_payment), balance)
