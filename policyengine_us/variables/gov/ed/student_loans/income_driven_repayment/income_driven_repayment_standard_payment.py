from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.student_loans.student_loan_amortization_helpers import (
    amortized_monthly_payment,
)


class income_driven_repayment_standard_payment(Variable):
    value_type = float
    entity = Person
    label = "Income-driven repayment 10-year standard payment cap"
    documentation = (
        "What the borrower would pay on the 10-year standard repayment plan "
        "on their own eligible loans, the most the borrower pays under the "
        "Income-Based Repayment and Pay As You Earn plans (20 U.S.C. "
        "1098e(b)(6)(A): 'for all loans made to the borrower under part B or "
        "D'). Eligible loans are Direct and FFEL loans other than parent PLUS "
        "loans and excepted consolidation loans, so this is the 10-year "
        "standard payment on the person's federal_student_loan_balance plus "
        "federal_ffel_loan_balance at their federal_student_loan_interest_rate. "
        "One standard plan minimum covers the Direct and FFEL loans together, "
        "and the payment is no more than the eligible balance. A joint filer's "
        "spouse's loans do not enter it: 34 CFR 685.209(e)(2)(i) counts them "
        "only in the (g) proration. The cap uses the current balance, not the "
        "balance when the borrower began paying under the plan."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/20/1098e#b_6_A",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(5)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(2)(ii)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(3)(ii)",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(1)",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans.standard_repayment
        eligible_balance = add(
            person,
            period.this_year,
            ["federal_student_loan_balance", "federal_ffel_loan_balance"],
        )
        annual_rate = person("federal_student_loan_interest_rate", period.this_year)
        number_of_payments = p.repayment_period * MONTHS_IN_YEAR
        amortized_payment = amortized_monthly_payment(
            eligible_balance, annual_rate, number_of_payments
        )
        # As in standard_repayment_payment, the minimum does not apply to a
        # final payment below it.
        return min_(max_(amortized_payment, p.minimum_payment), eligible_balance)
