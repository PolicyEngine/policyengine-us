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
        "borrower with a Direct Loan made on or after July 1, 2026. The plan "
        "repays all of the borrower's Direct Loans, Parent PLUS loans "
        "included (20 U.S.C. 1087e(d)(7)(A), (C), (E)), so the total of "
        "federal_student_loan_balance and federal_parent_plus_loan_balance "
        "sets the repayment period of 10, 15, 20 or 25 years, and the payment "
        "amortizes that total at federal_student_loan_interest_rate, which "
        "stands in for the Parent PLUS loans' rate too. It is at least the "
        "plan minimum, except that a total below the minimum is paid in full. "
        "The statute sets the period by the outstanding principal when the "
        "borrower enters repayment. The current balance, principal and "
        "interest, stands in for that principal, so accrued interest can push "
        "a borrower into the next tier: $24,999 of principal and $1 of "
        "interest repays over 15 years instead of 10. Zero for borrowers with "
        "no Direct Loan made on or after July 1, 2026, who use the 10-year "
        "standard plan (standard_repayment_payment)."
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
        # 20 U.S.C. 1087e(d)(7)(A)(i)(II) sets the period by "the total
        # outstanding principal of all loans of the borrower made under this
        # part", which includes Parent PLUS loans.
        balance = add(
            person,
            period.this_year,
            ["federal_student_loan_balance", "federal_parent_plus_loan_balance"],
        )
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
