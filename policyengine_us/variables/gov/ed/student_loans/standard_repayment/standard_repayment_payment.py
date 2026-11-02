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
        "when the loans entered repayment. A borrower with a Direct Loan made "
        "on or after July 1, 2026 cannot use this plan and repays under the "
        "tiered standard plan instead (tiered_standard_repayment_payment)."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(1)",
        "https://www.govinfo.gov/content/pkg/FR-2026-05-01/pdf/2026-08556.pdf#page=119",
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
        payment = min_(max_(amortized_payment, p.minimum_payment), balance)
        # 20 U.S.C. 1087e(d)(6)-(7) and 34 CFR 685.208(b)(1) limit this plan to
        # borrowers with no Direct Loan made on or after July 1, 2026.
        has_new_loan = person(
            "has_federal_student_loan_made_on_or_after_2026_07_01", period.this_year
        )
        return where(has_new_loan, 0, payment)
