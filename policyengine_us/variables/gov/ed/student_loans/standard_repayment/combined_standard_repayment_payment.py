from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.student_loans.student_loan_amortization_helpers import (
    direct_standard_amortized_payment,
    parent_plus_standard_amortized_payment,
)


class combined_standard_repayment_payment(Variable):
    value_type = float
    entity = Person
    label = "Combined Direct and parent PLUS standard repayment plan monthly payment"
    documentation = (
        "Monthly payment for a borrower with all of their Direct Loans "
        "(federal_student_loan_balance) and parent PLUS loans "
        "(federal_parent_plus_loan_balance) on the standard repayment plan. "
        "34 CFR 685.208(b)(1) puts Direct Subsidized, Unsubsidized and PLUS "
        "loans on one 10-year plan, and (b)(1)(ii) sets its $50 minimum on "
        "the borrower's payments, so the two level payments are added before "
        "one minimum applies, and the total is no more than the two balances. "
        "A Direct Consolidation Loan that repaid parent PLUS loans and "
        "entered repayment on or after July 1, 2006 "
        "(federal_parent_plus_loan_is_consolidated) repays under 685.208(b)(2), "
        "a separate plan with its own minimum in (b)(2)(ii), so for that "
        "borrower this is the sum of standard_repayment_payment and "
        "parent_plus_standard_repayment_payment. FFEL loans are not "
        "included. A borrower who holds Direct Loans on one plan and parent "
        "PLUS loans on another, such as an income-driven plan for the Direct "
        "Loans, is not modeled here; the two separate variables stay the "
        "right read for them. A borrower with a Direct Loan made on or after "
        "July 1, 2026 cannot use these plans and repays under the tiered "
        "standard plan (tiered_standard_repayment_payment), so this is zero "
        "for them."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(1)",
        "https://www.ecfr.gov/current/title-34/section-685.208#p-685.208(b)(2)",
        "https://www.law.cornell.edu/uscode/text/20/1087e#d_1_A",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.ed.student_loans.standard_repayment
        direct_balance = person("federal_student_loan_balance", period.this_year)
        parent_plus_balance = person(
            "federal_parent_plus_loan_balance", period.this_year
        )
        amortized_payment = direct_standard_amortized_payment(
            person, period, parameters
        ) + parent_plus_standard_amortized_payment(person, period, parameters)
        # 685.208(b)(1)(ii): one minimum on all of the borrower's payments
        # under the plan, except a final payment below it.
        one_plan_payment = min_(
            max_(amortized_payment, p.minimum_payment),
            direct_balance + parent_plus_balance,
        )
        # 685.208(b)(2): a consolidation loan repays under its own plan, with
        # its own (b)(2)(ii) minimum.
        is_consolidated = person(
            "federal_parent_plus_loan_is_consolidated", period.this_year
        )
        two_plan_payment = person("standard_repayment_payment", period) + person(
            "parent_plus_standard_repayment_payment", period
        )
        payment = where(is_consolidated, two_plan_payment, one_plan_payment)
        # 20 U.S.C. 1087e(d)(1) and (d)(7)(A) and 34 CFR 685.208(b)(1)-(2)
        # limit these plans to borrowers with no Direct Loan made on or after
        # July 1, 2026.
        has_new_loan = person(
            "has_federal_student_loan_made_on_or_after_2026_07_01", period.this_year
        )
        return where(has_new_loan, 0, payment)
