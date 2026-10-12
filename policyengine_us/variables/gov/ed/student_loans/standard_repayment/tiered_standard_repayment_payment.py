from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.student_loans.student_loan_amortization_helpers import (
    amortized_monthly_payment,
)


class tiered_standard_repayment_payment(Variable):
    value_type = float
    entity = Person
    label = "Tiered standard repayment plan monthly payment"
    documentation = (
        "Fixed monthly payment under the tiered standard repayment plan for a "
        "borrower with a Direct Loan made on or after July 1, 2026. The "
        "repayment period is 10, 15, 20 or 25 years depending on the "
        "borrower's total Direct Loan balance, and the payment amortizes that "
        "balance at the loans' interest rate. It is at least the plan minimum, "
        "except that a balance below the minimum is paid in full. The current "
        "balance stands in for the balance when the borrower entered "
        "repayment, and Parent PLUS loans (federal_parent_plus_loan_balance) "
        "are not included. Zero for borrowers with no Direct Loan made on or "
        "after July 1, 2026, who use the 10-year standard plan "
        "(standard_repayment_payment)."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=268",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(8)",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(c)(1)",
        "https://www.govinfo.gov/content/pkg/FR-2026-05-01/pdf/2026-08556.pdf#page=120",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans.tiered_standard_repayment
        balance = person("federal_student_loan_balance", period.this_year)
        annual_rate = person("federal_student_loan_interest_rate", period.this_year)
        repayment_period = p.repayment_period.calc(balance)
        number_of_payments = repayment_period * MONTHS_IN_YEAR
        amortized_payment = amortized_monthly_payment(
            balance, annual_rate, number_of_payments
        )
        # A balance below the minimum is paid in full.
        payment = min_(max_(amortized_payment, p.minimum_payment), balance)
        has_new_loan = person(
            "has_federal_student_loan_made_on_or_after_2026_07_01", period.this_year
        )
        return where(has_new_loan, payment, 0)
