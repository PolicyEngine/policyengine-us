from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.student_loans.student_loan_amortization_helpers import (
    amortized_monthly_payment,
)


class standard_repayment_payment(Variable):
    value_type = float
    entity = Person
    label = "Standard repayment plan monthly payment"
    documentation = (
        "Fixed monthly payment that repays the person's federal student loan "
        "balance over the 10-year standard repayment plan at the loans' "
        "interest rate, at least the plan minimum and no more than the "
        "balance. The payment amortizes the current balance, not the balance "
        "when the loans entered repayment. Loans made on or after July 1, "
        "2026, which repay under the tiered standard plan, are not modeled."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(1)",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans.standard_repayment
        balance = person("federal_student_loan_balance", period.this_year)
        annual_rate = person("federal_student_loan_interest_rate", period.this_year)
        number_of_payments = p.repayment_period * MONTHS_IN_YEAR
        amortized_payment = amortized_monthly_payment(
            balance, annual_rate, number_of_payments
        )
        # The minimum does not apply to a final payment below it.
        return min_(max_(amortized_payment, p.minimum_payment), balance)
